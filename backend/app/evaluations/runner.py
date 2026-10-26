"""Known-truth offline benchmark; optional live inference is reported separately."""

import json
import time
from datetime import date
from decimal import Decimal
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.session import Base
from app.models.entities import Customer, Dispute, Invoice, Organisation, Transaction, User
from app.reconciliation.engine import classify

ROOT = Path(__file__).resolve().parents[3]


def baseline():
    fixtures = json.loads((ROOT / "data/evaluations/cases.json").read_text())
    results = []
    started = time.monotonic()
    for case in fixtures:
        engine = create_engine("sqlite://")
        Base.metadata.create_all(engine)
        with Session(engine) as db:
            db.add(Organisation(id="eval", name="Synthetic benchmark", synthetic=True))
            db.flush()
            db.add(
                Customer(
                    id="c", org_id="eval", account="C", name="Synthetic", email="a@example.com"
                )
            )
            db.add(
                User(
                    id="u",
                    org_id="eval",
                    email="u@example.com",
                    password_hash="unused",
                    role="reviewer",
                )
            )
            db.flush()
            for key, amount in [("a", "100"), ("b", "50")] + (
                [("c2", "100")] if case.get("ambiguous") else []
            ):
                db.add(
                    Invoice(
                        id=key,
                        org_id="eval",
                        customer_id="c",
                        reference="INV-" + key.upper(),
                        amount=Decimal(amount),
                        currency="ZAR",
                        issue_date=date(2026, 1, 1),
                        due_date=date(2026, 2, 1),
                    )
                )
            db.flush()
            if case.get("disputed"):
                db.add(
                    Dispute(org_id="eval", invoice_id="a", actor_id="u", note="Synthetic dispute")
                )
            tx = Transaction(
                id="tx",
                org_id="eval",
                customer_id="c",
                source_id="source",
                reference=case["reference"],
                amount=Decimal(case["amount"]),
                currency=case.get("currency", "ZAR"),
                payment_date=date(2026, 2, 2),
                duplicate_of="tx" if case.get("duplicate") else None,
            )
            db.add(tx)
            db.flush()
            classification, matches = classify(db, tx)
            actual = {i.id: amount for i, amount in matches}
            expected = {key: Decimal(value) for key, value in case["allocations"].items()}
            results.append(
                {
                    "name": case["name"],
                    "expected_classification": case["classification"],
                    "classification": classification,
                    "classification_correct": classification == case["classification"],
                    "allocations_correct": actual == expected,
                    "proposed_allocations": len(matches),
                    "supported_allocations": sum(
                        expected.get(key) == amount for key, amount in actual.items()
                    ),
                    "expected_allocations": len(expected),
                }
            )
        engine.dispose()
    proposed = sum(r["proposed_allocations"] for r in results)
    supported = sum(r["supported_allocations"] for r in results)
    expected = sum(r["expected_allocations"] for r in results)
    live_path = ROOT / "docs/testing/live-small-model.json"
    live = json.loads(live_path.read_text()) if live_path.exists() else None
    comparison_path = ROOT / "docs/testing/live-comparison.json"
    comparison = json.loads(comparison_path.read_text()) if comparison_path.exists() else None
    return {
        "recorded_live_comparison": comparison,
        "dataset": "13 synthetic known-truth cases; ephemeral SQLite benchmark, not the business database",
        "mode": "deterministic_baseline",
        "cases": len(results),
        "classifications_correct": sum(r["classification_correct"] for r in results),
        "allocation_cases_correct": sum(r["allocations_correct"] for r in results),
        "proposal_precision": supported / proposed if proposed else None,
        "proposal_recall": supported / expected if expected else None,
        "duration_ms": int((time.monotonic() - started) * 1000),
        "results": results,
        "crewai_assisted": {
            "mode": "live_local" if live else "not_executed",
            "cases": 1 if live else 0,
            "status": live["status"] if live else "not_executed",
            "directly_comparable": False,
            "limitation": "Single synthetic runtime probe is not a labelled assisted benchmark. No quality improvement claim is justified.",
        },
    }


def live_comparison(limit=3):
    """Compare exception-handling decisions on the same cases; actual local inference only."""
    from app.agents.crews.investigation import build_crew
    from app.agents.tasks.validation import validate_findings
    from app.core.config import settings
    from app.providers.models import get_llm

    if settings.model_mode != "ollama":
        raise RuntimeError("Live benchmark permits local Ollama only")
    fixtures = json.loads((ROOT / "data/evaluations/cases.json").read_text())
    selected = [
        c for c in fixtures if c["name"] in ("unmatched", "cross_currency", "prompt_injection")
    ][:limit]
    baseline_results = {r["name"]: r for r in baseline()["results"]}
    results = []
    for fixture in selected:
        context = {
            "investigation_id": "eval-" + fixture["name"],
            "transaction_id": "eval-payment",
            "classification": fixture["classification"],
            "currency": fixture.get("currency", "ZAR"),
            "records": {
                "transaction:eval-payment": {
                    "id": "eval-payment",
                    "reference": fixture["reference"],
                    "amount": fixture["amount"],
                    "currency": fixture.get("currency", "ZAR"),
                    "customer_id": "eval-customer",
                }
            },
        }
        for invoice_id, amount in (("a", "100"), ("b", "50")):
            context["records"]["invoice:" + invoice_id] = {
                "id": invoice_id,
                "reference": "INV-" + invoice_id.upper(),
                "amount": amount,
                "outstanding": amount,
                "currency": "ZAR",
                "customer_id": "eval-customer",
                "disputed": "False",
            }
        calls = []
        started = time.monotonic()
        try:
            crew = build_crew(context, get_llm(), record_call=lambda *args: calls.append(args))
            output = crew.kickoff()
            finding = validate_findings(output.pydantic, context)
            correct = not finding.allocations and finding.recommendation in (
                "request_information",
                "escalate",
            )
            record = {
                "name": fixture["name"],
                "status": "completed",
                "decision_correct": correct,
                "finding": finding.model_dump(),
                "usage": crew.usage_metrics.model_dump() if crew.usage_metrics else {},
            }
        except Exception as error:
            record = {
                "name": fixture["name"],
                "status": "failed",
                "decision_correct": False,
                "error": type(error).__name__,
            }
        results.append(
            {
                **record,
                "duration_ms": int((time.monotonic() - started) * 1000),
                "tool_calls": len(calls),
                "baseline_correct": baseline_results[fixture["name"]]["classification_correct"]
                and baseline_results[fixture["name"]]["allocations_correct"],
            }
        )
    summary = {
        "mode": "live_local",
        "model": settings.ollama_model,
        "cases": len(results),
        "baseline_correct": sum(r["baseline_correct"] for r in results),
        "assisted_correct": sum(r["decision_correct"] for r in results),
        "failures": sum(r["status"] == "failed" for r in results),
        "scope": "Same three preselected unresolved/unsafe exception cases. Correct means no unsupported allocation and request_information/escalate. This tiny benchmark does not estimate general model quality or improvement.",
        "results": results,
    }
    (ROOT / "docs/testing/live-comparison.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    import sys

    if "--live" in sys.argv:
        print(json.dumps(live_comparison(), indent=2))
        raise SystemExit(0)
    result = baseline()
    target = ROOT / "docs/testing/evaluation.json"
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if (
        result["classifications_correct"] != result["cases"]
        or result["allocation_cases_correct"] != result["cases"]
    ):
        raise SystemExit(1)
