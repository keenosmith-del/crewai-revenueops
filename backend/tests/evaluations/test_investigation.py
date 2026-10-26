import json

import pytest
from crewai import BaseLLM
from pydantic import Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.agents.schemas.outputs import Findings
from app.core.config import settings
from app.evaluations.investigation import (
    digest,
    evidence_and_baseline,
    fixture,
    load_cases,
    parent_run,
    run_case,
    score,
    summary,
    verify_financial_result,
)
from app.models.entities import Allocation


@pytest.mark.parametrize("case", load_cases(), ids=lambda case: case["id"])
def test_same_frozen_evidence_excludes_labels_and_never_posts(case):
    with fixture(case) as engine:
        context, baseline = evidence_and_baseline(engine, case)
        assert "ground_truth" not in json.dumps(context)
        assert "rationale" not in json.dumps(context)
        assert {key for key in context["records"] if key.startswith("invoice:")} == {
            "invoice:" + i["id"] for i in case["invoices"]
        }
        assert {key for key in context["records"] if key.startswith("dispute:")} == {
            "dispute:" + i["id"] for i in case["notes"]
        }
        with Session(engine) as db:
            assert db.scalar(select(func.count()).select_from(Allocation)) == 0
    with fixture(case) as engine:
        repeated, _ = evidence_and_baseline(engine, case)
        assert digest(repeated) == digest(context)
    assert score(case, case["ground_truth"]["decision"], case["ground_truth"]["allocations"])[
        "correct"
    ]


def test_baseline_exposes_intent_gap_without_claiming_posted_money():
    results = []
    for case in load_cases():
        with fixture(case) as engine:
            _, baseline = evidence_and_baseline(engine, case)
        results.append({"ground_truth": case["ground_truth"], "baseline": baseline})
    measured = summary(results, "baseline")
    assert measured["exact_decisions_correct"] == 1
    assert measured["abstentions"] == 3
    assert measured["wrong_target_or_amount"] == 1
    assert measured["accuracy"] == 0.25


def test_failure_stays_in_accuracy_denominator():
    case = load_cases()[0]
    failed = {
        "ground_truth": case["ground_truth"],
        "assisted": {"status": "timeout", "score": {"correct": False}},
    }
    result = summary([failed], "assisted")
    assert result["accuracy"] == 0 and result["failures"] == 1
    assert result["abstentions"] == 0 and result["allocation_precision"] is None


class FixtureLLM(BaseLLM):
    payload: dict = Field(default_factory=dict)

    def call(self, messages, **kwargs):
        return "Final Answer: " + json.dumps(self.payload)

    def supports_function_calling(self):
        return False


def test_actual_flow_with_mocked_inference_is_labelled_and_financially_validated():
    case = load_cases()[0]
    payload = {
        "investigation_id": "eval-" + case["id"],
        "transaction_id": "payment",
        "currency": "ZAR",
        "allocations": case["ground_truth"]["allocations"],
        "summary": "Reviewed remittance history identifies the intended invoice.",
        "evidence": [
            {"reference": "invoice:a", "field": "reference", "value": "SYN-INV-1032"},
            {"reference": "dispute:note-a", "field": "note", "value": case["notes"][0]["note"]},
        ],
        "uncertainty": "medium",
        "recommendation": "propose_allocation",
        "required_human_action": "Review remittance and approve only after independent verification",
    }
    events = []
    result = run_case(
        case, events.append, llm=FixtureLLM(model="mocked-evaluation-contract", payload=payload)
    )
    assert result["assisted"]["mode"] == "mocked_contract_test"
    assert result["assisted"]["score"]["correct"]
    assert result["ledger_allocations_written"] == 0
    assert len([event for event in events if event["kind"] == "task_completed"]) == 2
    assert result["assisted"]["crew_id"]


def test_financial_checks_reject_schema_valid_overallocation():
    case = load_cases()[0]
    finding = Findings(
        investigation_id="eval-" + case["id"],
        transaction_id="payment",
        currency="ZAR",
        allocations=[{"invoice_id": "a", "amount": "101.00"}],
        summary="Invalid proposed amount must be rejected.",
        evidence=[{"reference": "invoice:a", "field": "reference", "value": "SYN-INV-1032"}],
        uncertainty="high",
        recommendation="propose_allocation",
        required_human_action="Do not allocate without financial checks",
    )
    from fastapi import HTTPException

    with fixture(case) as engine:
        with pytest.raises(HTTPException):
            verify_financial_result(engine, case, finding)
        with Session(engine) as db:
            assert db.scalar(select(func.count()).select_from(Allocation)) == 0


def test_live_benchmark_cannot_use_hosted_models(monkeypatch):
    monkeypatch.setattr(settings, "model_mode", "hosted")
    monkeypatch.setattr(settings, "hosted_enabled", True)
    with pytest.raises(ValueError, match="hosted models are prohibited"):
        parent_run(live=True)
