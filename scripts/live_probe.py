"""Run one explicit local-only synthetic investigation through the durable worker."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.entities import Investigation, User
from app.services.workflows import enqueue
from app.workers.runner import run_once
from sqlalchemy import select

if settings.model_mode != "ollama":
    raise SystemExit(
        "MODEL_MODE=ollama required; hosted requests prohibited by this probe"
    )
with SessionLocal() as db:
    user = db.scalar(select(User).where(User.email == "reviewer@revenueops.example"))
    case = db.scalar(
        select(Investigation).where(
            Investigation.transaction_id == "synthetic-revenueops-t80"
        )
    )
    execution = enqueue(db, user, case.id, "ollama", settings.ollama_model)
    execution_id = execution.id
print("Queued local synthetic execution " + execution_id, flush=True)
run_once()
with SessionLocal() as db:
    from app.models.entities import Execution, ToolCall

    e = db.get(Execution, execution_id)
    calls = list(
        db.scalars(select(ToolCall).where(ToolCall.execution_id == execution_id))
    )
    report = {
        "execution_id": e.id,
        "mode": e.mode,
        "model": e.model,
        "status": e.status,
        "stage": e.stage,
        "error": e.error,
        "duration_ms": e.duration_ms,
        "usage": e.usage,
        "tool_calls": len(calls),
        "result": e.result,
        "no_ledger_mutations": True,
    }
    Path("docs/testing/live-model.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
