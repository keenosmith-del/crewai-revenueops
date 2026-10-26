"""Frozen ambiguous-payment benchmark. Labels never enter agent context; no ledger posting."""

import argparse
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import date
from decimal import Decimal
from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.accounting.money import money
from app.db.session import Base
from app.models.entities import (
    Allocation,
    Batch,
    Customer,
    Dispute,
    Investigation,
    Invoice,
    Organisation,
    Transaction,
    User,
)
from app.reconciliation.engine import classify
from app.services.evidence import snapshot
from app.services.workflows import validate_allocations

ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "data/evaluations/ambiguous-cases.json"
MODULE = "app.evaluations.investigation"


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def load_cases():
    dataset = json.loads(DATASET.read_text())
    if dataset["synthetic"] is not True or len({c["id"] for c in dataset["cases"]}) != len(
        dataset["cases"]
    ):
        raise ValueError("Unique labelled synthetic cases required")
    for case in dataset["cases"]:
        money(case["payment"]["amount"], "ZAR")
        if len({i["id"] for i in case["invoices"]}) != len(case["invoices"]):
            raise ValueError("Duplicate fixture invoice ID")
        for invoice in case["invoices"]:
            money(invoice["amount"], "ZAR")
        truth = case["ground_truth"]
        if truth["decision"] not in ("propose_allocation", "abstain") or bool(
            truth["allocations"]
        ) != (truth["decision"] == "propose_allocation"):
            raise ValueError("Contradictory ground truth")
        for allocation in truth["allocations"]:
            money(allocation["amount"], "ZAR")
    return dataset["cases"]


@contextmanager
def fixture(case):
    # This engine never uses DATABASE_URL/SessionLocal or the operational ledger.
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(
            Organisation(id="eval-org", name="Synthetic investigation benchmark", synthetic=True)
        )
        db.flush()
        db.add(
            Customer(
                id="eval-customer",
                org_id="eval-org",
                name="Synthetic Customer",
                account="SYN-EVAL",
                email="synthetic@customer.example",
            )
        )
        db.add(
            User(
                id="eval-user",
                org_id="eval-org",
                email="synthetic@reviewer.example",
                password_hash="disabled",
                role="reviewer",
                active=False,
            )
        )
        db.flush()
        for item in case["invoices"]:
            db.add(
                Invoice(
                    **item,
                    org_id="eval-org",
                    customer_id="eval-customer",
                    currency="ZAR",
                    issue_date=date(2026, 1, 1),
                    due_date=date(2026, 2, 1),
                )
            )
        db.add(
            Transaction(
                id="payment",
                org_id="eval-org",
                customer_id="eval-customer",
                currency="ZAR",
                payment_date=date(2026, 2, 2),
                **case["payment"],
            )
        )
        db.flush()
        for note in case["notes"]:
            db.add(Dispute(**note, org_id="eval-org", actor_id="eval-user"))
        db.flush()
        category, matches = classify(db, db.get(Transaction, "payment"))
        db.add(Batch(id="eval-batch", org_id="eval-org", summary={}))
        db.flush()
        db.add(
            Investigation(
                id="eval-" + case["id"],
                org_id="eval-org",
                batch_id="eval-batch",
                transaction_id="payment",
                classification=category,
                proposal={
                    "allocations": [
                        {"invoice_id": i.id, "amount": str(amount)} for i, amount in matches
                    ]
                },
            )
        )
        db.commit()
    try:
        yield engine
    finally:
        engine.dispose()


def evidence_and_baseline(engine, case):
    with Session(engine) as db:
        investigation = db.get(Investigation, "eval-" + case["id"])
        context = snapshot(db, "eval-org", investigation.id)
        items = investigation.proposal["allocations"]
        if items:
            validate_allocations(db, investigation, items)
        baseline = {
            "classification": investigation.classification,
            "decision": "propose_allocation" if items else "abstain",
            "allocations": items,
        }
        baseline["score"] = score(case, baseline["decision"], items)
        assert db.scalar(select(func.count()).select_from(Allocation)) == 0
    return context, baseline


def canonical(items):
    return sorted((item["invoice_id"], Decimal(item["amount"])) for item in items)


def score(case, decision, allocations):
    expected = case["ground_truth"]
    actual = canonical(allocations)
    truth = canonical(expected["allocations"])
    return {
        "correct": decision == expected["decision"] and actual == truth,
        "abstained": decision == "abstain",
        "proposed": len(actual),
        "correct_allocations": sum(item in truth for item in actual),
        "expected_allocations": len(truth),
        "wrong_target_or_amount": len(actual) - sum(item in truth for item in actual),
    }


def verify_financial_result(engine, case, finding):
    with Session(engine) as db:
        record = db.get(Investigation, "eval-" + case["id"])
        if finding.allocations:
            validate_allocations(db, record, [a.model_dump() for a in finding.allocations])
        if db.scalar(select(func.count()).select_from(Allocation)) != 0:
            raise ValueError("Benchmark must never post allocations")


def run_case(case, record_event, llm=None):
    from app.agents.tasks.validation import validate_findings
    from app.core.config import settings
    from app.flows.reconciliation import ReconciliationFlow
    from app.providers.models import get_llm

    if llm is None and settings.model_mode != "ollama":
        raise ValueError("Only explicit local Ollama inference is permitted")
    started = time.monotonic()
    phase = "provider"
    with fixture(case) as engine:
        context, baseline = evidence_and_baseline(engine, case)
        result = {
            "case_id": case["id"],
            "evidence_sha256": digest(context),
            "ground_truth": case["ground_truth"],
            "baseline": baseline,
        }
        flow = None
        try:
            provider = llm if llm is not None else get_llm()
            phase = "crewai_inference"

            def tool_call(name, record_id, status, duration_ms):
                record_event(
                    {
                        "kind": "tool_call",
                        "name": name,
                        "record_id": record_id,
                        "status": status,
                        "duration_ms": duration_ms,
                    }
                )

            def task_done(output):
                record_event({"kind": "task_completed", "task": output.name, "agent": output.agent})

            # All DB sessions are closed before CrewAI starts. Tools receive only the snapshot.
            flow = ReconciliationFlow(
                context=context, llm=provider, record_call=tool_call, task_callback=task_done
            )
            flow.kickoff()
            phase = "output_validation"
            finding = validate_findings(flow.state.result, context)
            phase = "financial_validation"
            verify_financial_result(engine, case, finding)
            decision = (
                "propose_allocation"
                if finding.recommendation == "propose_allocation"
                else "abstain"
                if finding.recommendation in ("request_information", "escalate")
                else "other"
            )
            result["assisted"] = {
                "mode": "mocked_contract_test" if llm is not None else "live_local",
                "status": "completed",
                "decision": decision,
                "findings": finding.model_dump(),
                "score": score(case, decision, [a.model_dump() for a in finding.allocations]),
                "usage": flow.state.usage,
                "crew_id": flow.state.crew_id,
            }
        except Exception as error:
            result["assisted"] = {
                "mode": "mocked_contract_test" if llm is not None else "live_local_attempt",
                "status": "failed",
                "failed_phase": phase,
                "crew_id": flow.state.crew_id if flow else None,
                "usage": flow.state.usage if flow else {},
                "error_type": type(error).__name__,
                "score": {"correct": False},
            }
        result["assisted"]["latency_ms"] = int((time.monotonic() - started) * 1000)
        result["ledger_allocations_written"] = 0
        return result


def summary(results, key):
    cases = [r[key] for r in results]
    successful = [r for r in cases if r.get("status", "completed") == "completed"]
    proposed = sum(r["score"].get("proposed", 0) for r in successful)
    correct_allocations = sum(r["score"].get("correct_allocations", 0) for r in successful)
    expected = sum(len(r["ground_truth"]["allocations"]) for r in results)
    return {
        "cases": len(cases),
        "exact_decisions_correct": sum(r["score"]["correct"] for r in cases),
        "accuracy": sum(r["score"]["correct"] for r in cases) / len(cases),
        "failures": len(cases) - len(successful),
        "abstentions": sum(r["score"].get("abstained", False) for r in successful),
        "proposed_allocations": proposed,
        "wrong_target_or_amount": sum(
            r["score"].get("wrong_target_or_amount", 0) for r in successful
        ),
        "allocation_precision": correct_allocations / proposed if proposed else None,
        "allocation_recall": correct_allocations / expected if expected else None,
    }


def parent_run(live=False, timeout=240):
    from app.core.config import settings

    if live and settings.model_mode != "ollama":
        raise ValueError("Set MODEL_MODE=ollama explicitly; hosted models are prohibited")
    records = []
    scratch = ROOT / ".runtime/evaluations"
    scratch.mkdir(parents=True, exist_ok=True)
    output = (
        ROOT
        / "docs/testing/iteration-009"
        / ("ambiguous-live.json" if live else "ambiguous-baseline.json")
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    for case in load_cases():
        with fixture(case) as engine:
            context, baseline = evidence_and_baseline(engine, case)
        record = {
            "case_id": case["id"],
            "evidence_sha256": digest(context),
            "ground_truth": case["ground_truth"],
            "baseline": baseline,
            "ledger_allocations_written": 0,
        }
        if live:
            with tempfile.TemporaryDirectory(dir=scratch) as directory:
                result_file, trace_file = (
                    Path(directory) / "result.json",
                    Path(directory) / "trace.jsonl",
                )
                env = {**os.environ, "PYTHONPATH": str(ROOT / "backend")}
                started = time.monotonic()
                process = subprocess.Popen(
                    [
                        sys.executable,
                        "-m",
                        MODULE,
                        "--live",
                        "--case",
                        case["id"],
                        "--result",
                        str(result_file),
                        "--trace",
                        str(trace_file),
                    ],
                    cwd=ROOT,
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                try:
                    process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                if result_file.exists():
                    child = json.loads(result_file.read_text())
                    if child["evidence_sha256"] != record["evidence_sha256"]:
                        raise ValueError("Baseline and assisted evidence diverged")
                    record = child
                else:
                    record["assisted"] = {
                        "mode": "live_local_attempt",
                        "status": "timeout" if process.returncode == -9 else "failed",
                        "error_type": "CaseTimeout"
                        if process.returncode == -9
                        else "ChildProcessFailure",
                        "score": {"correct": False},
                        "latency_ms": int((time.monotonic() - started) * 1000),
                    }
                events = (
                    [json.loads(line) for line in trace_file.read_text().splitlines()]
                    if trace_file.exists()
                    else []
                )
                record["assisted"]["tool_calls"] = [e for e in events if e["kind"] == "tool_call"]
                record["assisted"]["completed_tasks"] = [
                    e for e in events if e["kind"] == "task_completed"
                ]
        records.append(record)
        report = {
            "synthetic": True,
            "mode": "live_local" if live else "deterministic_baseline",
            "model": settings.ollama_model if live else None,
            "dataset_sha256": hashlib.sha256(DATASET.read_bytes()).hexdigest(),
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "crewai_version": importlib.metadata.version("crewai"),
            "timeout_seconds_per_case": timeout if live else None,
            "ground_truth_excluded_from_model_context": True,
            "same_evidence_hash_enforced": True,
            "attempts_per_case": 1,
            "results": records,
            "baseline": summary(records, "baseline"),
            "limitations": [
                "Four hand-authored synthetic cases, one model run each; not representative accuracy or an improvement guarantee.",
                "Wrong-target proposals differ from financial-policy violations; every operational proposal still requires human review.",
                "Failures remain in the accuracy denominator. Framework retries are unchanged; token usage may include estimates.",
                "No application database, ledger posting, hosted inference or external communications are used.",
            ],
        }
        if live:
            report["assisted"] = summary(records, "assisted")
        output.write_text(json.dumps(report, indent=2) + "\n")
        print(
            f"{case['id']}: "
            + (record["assisted"]["status"] if live else baseline["classification"]),
            flush=True,
        )
    return report


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--baseline", action="store_true")
    mode.add_argument("--live", action="store_true")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--case", choices=[c["id"] for c in load_cases()], help=argparse.SUPPRESS)
    parser.add_argument("--result", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--trace", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not 10 <= args.timeout <= 600:
        parser.error("Timeout must be between 10 and 600 seconds")
    if args.case:
        if not args.live or any(
            p is None or not p.resolve().is_relative_to(ROOT / ".runtime/evaluations")
            for p in (args.result, args.trace)
        ):
            parser.error("Child outputs must be confined to evaluation scratch storage")

        def record_event(event):
            with args.trace.open("a") as stream:
                stream.write(json.dumps(event) + "\n")

        case = next(c for c in load_cases() if c["id"] == args.case)
        args.result.write_text(json.dumps(run_case(case, record_event), indent=2) + "\n")
    else:
        report = parent_run(live=args.live, timeout=args.timeout)
        print(
            json.dumps(
                {key: report[key] for key in ("baseline", "assisted") if key in report}, indent=2
            )
        )


if __name__ == "__main__":
    main()
