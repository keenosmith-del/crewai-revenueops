"""PostgreSQL leased outbox. Child process bounds inference; fencing prevents stale writes."""

import subprocess
import sys
import time
from datetime import timedelta
from uuid import uuid4

from sqlalchemy import or_, select

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.entities import (
    Audit,
    Draft,
    Execution,
    Investigation,
    Invoice,
    Organisation,
    ToolCall,
    now,
)
from app.repositories.records import get
from app.services.evidence import snapshot
from app.services.ledger import disputed, outstanding
from app.services.workflows import validate_allocations


class LostLease(RuntimeError):
    pass


def owned(db, execution_id, lease):
    execution = db.scalar(select(Execution).where(Execution.id == execution_id).with_for_update())
    if not execution or execution.lease_token != lease or execution.status != "running":
        raise LostLease("Execution ownership changed")
    return execution


def claim(db):
    job = db.scalar(
        select(Execution)
        .where(
            or_(
                Execution.status == "queued",
                (Execution.status == "running") & (Execution.lease_until < now()),
            )
        )
        .order_by(Execution.created_at)
        .with_for_update(skip_locked=True)
        .limit(1)
    )
    if not job:
        db.rollback()
        return None
    if job.attempts >= 3:
        job.status, job.stage, job.error = "failed", "failed", "Retry limit exceeded"
        case = get(db, Investigation, job.investigation_id, job.org_id)
        case.status = "failed"
        db.commit()
        return None
    job.status = "running"
    job.attempts += 1
    job.lease_token = str(uuid4())
    job.lease_until = now() + timedelta(seconds=90)
    db.commit()
    return job.id, job.lease_token


def execute(execution_id, lease):
    from app.flows.reconciliation import ReconciliationFlow
    from app.providers.models import get_llm

    started = time.monotonic()
    with SessionLocal() as db:
        execution = owned(db, execution_id, lease)
        if execution.mode != settings.model_mode:
            raise RuntimeError("Configured provider changed since enqueue")
        context = snapshot(db, execution.org_id, execution.investigation_id)
        context["purpose"] = execution.checkpoint.get("purpose", "investigation")
        saved = execution.checkpoint.get("flow", {})
        org, case_id = execution.org_id, execution.investigation_id
        actor_id = execution.checkpoint["actor_id"]
        db.commit()

    def checkpoint(state):
        with SessionLocal() as db:
            e = owned(db, execution_id, lease)
            e.checkpoint = {**e.checkpoint, "flow": state}
            e.stage = state["stage"]
            db.commit()

    def record_call(name, record_id, status, duration):
        with SessionLocal() as db:
            owned(db, execution_id, lease)
            db.add(
                ToolCall(
                    org_id=org,
                    execution_id=execution_id,
                    name=name,
                    record_id=record_id,
                    status=status,
                    duration_ms=duration,
                )
            )
            db.commit()

    def task_callback(output):
        with SessionLocal() as db:
            owned(db, execution_id, lease)
            db.add(
                Audit(
                    org_id=org,
                    actor_id="worker",
                    action="agent.task_completed",
                    record_id=execution_id,
                    detail={
                        "agent": output.agent,
                        "task": output.name,
                        "structured_output": output.pydantic.model_dump()
                        if output.pydantic
                        else {},
                        "mode": settings.model_mode,
                    },
                )
            )
            db.commit()

    llm = (
        None
        if context["classification"] == "exact" and context["purpose"] != "collections"
        else get_llm()
    )
    flow = ReconciliationFlow(
        context=context,
        llm=llm,
        checkpoint=checkpoint,
        record_call=record_call,
        task_callback=task_callback,
    )
    inputs = {**saved, "id": execution_id}
    flow.kickoff(inputs=inputs)
    result = flow.state.result
    with SessionLocal() as db:
        db.scalar(select(Organisation).where(Organisation.id == org).with_for_update())
        e = owned(db, execution_id, lease)
        case = get(db, Investigation, case_id, org, lock=True)
        if result:
            if result.get("allocations"):
                validate_allocations(db, case, result["allocations"], lock=True)
            case.proposal = {**result, "source": "crewai"}
            case.explanation = result["summary"][:1000]
            if context["purpose"] == "collections" and result.get("draft_message"):
                # Only exact authoritative eligibility can create an internal draft.
                eligible = [
                    get(db, Invoice, key.split(":", 1)[1], org, lock=True)
                    for key in context["records"]
                    if key.startswith("invoice:")
                ]
                from datetime import date

                eligible = [
                    i
                    for i in eligible
                    if i.due_date < date.today() and outstanding(db, i) > 0 and not disputed(db, i)
                ]
                if len(eligible) != 1:
                    raise ValueError(
                        "AI collection drafts require one eligible invoice; use the explicit invoice template otherwise"
                    )
                db.add(
                    Draft(
                        org_id=org,
                        invoice_id=eligible[0].id,
                        actor_id=actor_id,
                        body=result["draft_message"],
                        source="crewai",
                    )
                )
        case.status = "human_review"
        e.result, e.status, e.stage = (
            result or {"mode": "deterministic_only"},
            "completed",
            "human_review",
        )
        e.usage = flow.state.usage
        e.duration_ms = int((time.monotonic() - started) * 1000)
        e.lease_until = None
        db.add(
            Audit(
                org_id=org,
                actor_id="worker",
                action="flow.completed",
                record_id=e.id,
                detail={"stage": e.stage, "mode": e.mode, "ledger_mutated": False},
            )
        )
        db.commit()


def fail(execution_id, lease, category):
    with SessionLocal() as db:
        try:
            e = owned(db, execution_id, lease)
        except LostLease:
            return
        e.status, e.stage, e.error = "failed", "failed", category
        case = get(db, Investigation, e.investigation_id, e.org_id)
        case.status = "failed"
        db.add(
            Audit(
                org_id=e.org_id,
                actor_id="worker",
                action="flow.failed",
                record_id=e.id,
                detail={"classification": category, "attempt": e.attempts},
            )
        )
        db.commit()


def run_once():
    with SessionLocal() as db:
        claimed = claim(db)
    if not claimed:
        return False
    execution_id, lease = claimed
    child = subprocess.Popen(
        [sys.executable, "-m", "app.workers.runner", "--execute", execution_id, lease],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    started = time.monotonic()
    while child.poll() is None:
        if time.monotonic() - started > 480:
            child.kill()
            child.wait()
            fail(execution_id, lease, "model_timeout")
            return True
        time.sleep(10)
        with SessionLocal() as db:
            try:
                e = owned(db, execution_id, lease)
                e.lease_until = now() + timedelta(seconds=90)
                db.commit()
            except LostLease:
                child.terminate()
                child.wait(timeout=10)
                break
    if child.returncode:
        fail(execution_id, lease, "model_or_validation_failure")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        try:
            execute(sys.argv[2], sys.argv[3])
        except Exception as exc:
            fail(sys.argv[2], sys.argv[3], type(exc).__name__)
            sys.exit(1)
    else:
        settings.validate_runtime()
        while True:
            if not run_once():
                time.sleep(2)
