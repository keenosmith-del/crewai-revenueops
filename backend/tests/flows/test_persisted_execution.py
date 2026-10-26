import json

from crewai import BaseLLM
from pydantic import Field
from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.entities import Allocation, Audit, Execution, Investigation
from app.services.workflows import enqueue, reconcile
from app.workers import runner


class FixtureLLM(BaseLLM):
    payload: dict = Field(default_factory=dict)

    def call(self, messages, **kwargs):
        return "Final Answer: " + json.dumps(self.payload)

    def supports_function_calling(self):
        return False


def test_worker_persists_and_resumes_without_provider_or_ledger_writes(db, user, monkeypatch):
    monkeypatch.setattr(settings, "model_mode", "ollama")
    monkeypatch.setattr(runner, "SessionLocal", sessionmaker(db.bind, expire_on_commit=False))
    reconcile(db, user)
    case = db.scalar(select(Investigation))
    case.classification = "unmatched"
    db.commit()
    execution = enqueue(db, user, case.id, "ollama", "fixture-model")
    payload = {
        "investigation_id": case.id,
        "transaction_id": "tx",
        "currency": "ZAR",
        "allocations": [],
        "summary": "Transaction requires a reviewer decision.",
        "evidence": [{"reference": "transaction:tx", "field": "reference", "value": "INV-001"}],
        "uncertainty": "high",
        "recommendation": "request_information",
        "missing_information": ["Verified allocation approval"],
        "validation_findings": [],
        "required_human_action": "Review the source evidence",
        "draft_message": None,
    }
    from app.providers import models

    monkeypatch.setattr(
        models, "get_llm", lambda: FixtureLLM(model="mocked-worker-contract", payload=payload)
    )
    identifier, lease = runner.claim(db)
    runner.execute(identifier, lease)
    db.expire_all()
    saved = db.get(Execution, execution.id)
    assert saved.status == "completed" and saved.result == payload
    assert saved.checkpoint["flow"]["stage"] == "human_review"
    assert saved.checkpoint["flow"]["crew_id"]
    assert (
        db.scalar(
            select(func.count()).select_from(Audit).where(Audit.action == "agent.task_completed")
        )
        == 2
    )
    assert db.scalar(select(func.count()).select_from(Allocation)) == 0

    # Simulate crash after checkpoint persistence but before terminal job commit.
    saved.status = "running"
    saved.lease_token = "resumed-owner"
    db.commit()

    def unavailable():
        raise AssertionError("A completed inference must not request a provider on resume")

    monkeypatch.setattr(models, "get_llm", unavailable)
    runner.execute(identifier, "resumed-owner")
    db.expire_all()
    assert db.get(Execution, identifier).status == "completed"
    assert (
        db.scalar(
            select(func.count()).select_from(Audit).where(Audit.action == "agent.task_completed")
        )
        == 2
    )
    assert db.scalar(select(func.count()).select_from(Allocation)) == 0


def test_worker_failure_records_duration_and_preserves_ledger(db, user, monkeypatch):
    monkeypatch.setattr(runner, "SessionLocal", sessionmaker(db.bind, expire_on_commit=False))
    reconcile(db, user)
    case = db.scalar(select(Investigation))
    enqueue(db, user, case.id, "ollama", "fixture-model")
    identifier, lease = runner.claim(db)
    runner.fail(identifier, lease, "synthetic_model_failure")
    db.expire_all()
    execution = db.get(Execution, identifier)
    assert execution.status == "failed" and execution.duration_ms is not None
    assert db.get(Investigation, case.id).status == "failed"
    assert db.scalar(select(func.count()).select_from(Allocation)) == 0
