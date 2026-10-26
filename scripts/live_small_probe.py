"""A tiny persisted synthetic case for local-model capability verification."""

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.entities import (
    Customer,
    Execution,
    Investigation,
    Invoice,
    Organisation,
    ToolCall,
    Transaction,
    User,
)
from app.services.workflows import enqueue, reconcile
from app.workers.runner import run_once
from sqlalchemy import select

if settings.model_mode != "ollama":
    raise SystemExit("Local Ollama only")
with SessionLocal() as db:
    if not db.get(Organisation, "synthetic-model-probe"):
        db.add(
            Organisation(
                id="synthetic-model-probe",
                name="Synthetic model capability probe",
                synthetic=True,
            )
        )
        db.flush()
        db.add(
            User(
                id="probe-reviewer",
                org_id="synthetic-model-probe",
                email="probe@revenueops.example",
                password_hash="disabled",
                role="reviewer",
                active=False,
            )
        )
        db.add(
            Customer(
                id="probe-customer",
                org_id="synthetic-model-probe",
                name="Synthetic Customer",
                account="PROBE",
                email="probe@customer.example",
            )
        )
        db.flush()
        db.add(
            Invoice(
                id="probe-invoice",
                org_id="synthetic-model-probe",
                customer_id="probe-customer",
                reference="PROBE-001",
                amount=100,
                currency="ZAR",
                issue_date=date(2026, 1, 1),
                due_date=date(2026, 2, 1),
            )
        )
        db.add(
            Transaction(
                id="probe-payment",
                org_id="synthetic-model-probe",
                customer_id="probe-customer",
                source_id="PROBE-TX",
                reference="No invoice reference",
                amount=25,
                currency="ZAR",
                payment_date=date(2026, 2, 2),
            )
        )
        db.commit()
    actor = db.get(User, "probe-reviewer")
    reconcile(db, actor)
    case = db.scalar(select(Investigation).where(Investigation.org_id == actor.org_id))
    e = enqueue(db, actor, case.id, "ollama", settings.ollama_model)
    execution_id = e.id
print("Queued small local synthetic case " + execution_id, flush=True)
run_once()
with SessionLocal() as db:
    e = db.get(Execution, execution_id)
    calls = list(
        db.scalars(select(ToolCall).where(ToolCall.execution_id == execution_id))
    )
    result = {
        "execution_id": e.id,
        "mode": e.mode,
        "adapter": "crewai_native_openai_to_local_ollama",
        "model": e.model,
        "status": e.status,
        "stage": e.stage,
        "error": e.error,
        "duration_ms": e.duration_ms,
        "usage": e.usage,
        "tool_calls": len(calls),
        "result": e.result,
        "ledger_mutations": 0,
        "benchmark_quality_verified": False,
    }
    Path("docs/testing/live-small-model.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result, indent=2))
