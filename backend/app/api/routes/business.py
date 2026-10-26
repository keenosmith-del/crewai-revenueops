import csv
import io
import json
from datetime import date
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Header,
    HTTPException,
    Query,
    Response,
    UploadFile,
)
from sqlalchemy import select

from app.core.config import settings
from app.db.session import get_db
from app.models.entities import (
    Allocation,
    Audit,
    Batch,
    Customer,
    Dispute,
    Draft,
    Execution,
    Import,
    Investigation,
    Invoice,
    Organisation,
    Review,
    ToolCall,
    Transaction,
)
from app.repositories.records import get, rows
from app.schemas.requests import Decision, DisputeInput, DraftDecision, DraftInput
from app.security.auth import current_user, operator, reviewer
from app.services import imports, workflows
from app.services.ledger import audit, disputed, outstanding
from app.services.reporting import present, report, serialize

router = APIRouter(tags=["Operations"])
MODELS = {
    "invoices": Invoice,
    "transactions": Transaction,
    "customers": Customer,
    "investigations": Investigation,
    "batches": Batch,
    "imports": Import,
    "drafts": Draft,
    "audit": Audit,
    "executions": Execution,
    "tool-calls": ToolCall,
    "allocations": Allocation,
    "reviews": Review,
    "disputes": Dispute,
}


@router.get("/dashboard")
def dashboard(
    currency: str = "ZAR",
    start: date | None = None,
    end: date | None = None,
    db=Depends(get_db),
    user=Depends(current_user),
):
    return report(db, user.org_id, currency, start, end)


@router.post("/imports/{kind}/preview")
async def preview(
    kind: str,
    file: Annotated[UploadFile, File()],
    mapping: Annotated[str, Form()] = "{}",
    db=Depends(get_db),
    user=Depends(operator),
):
    if not (file.filename or "").lower().endswith(".csv") or file.content_type not in (
        "text/csv",
        "application/csv",
        "application/vnd.ms-excel",
        "application/octet-stream",
    ):
        raise HTTPException(422, "Upload a UTF-8 CSV file")
    try:
        columns = json.loads(mapping)
        if not isinstance(columns, dict) or any(
            not isinstance(k, str) or not isinstance(v, str) for k, v in columns.items()
        ):
            raise ValueError()
    except (ValueError, TypeError) as exc:
        raise HTTPException(422, "Column mapping must be a JSON object of strings") from exc
    content = await file.read(2_000_001)
    return serialize(imports.preview(db, user, kind, content, file.filename, columns))


@router.post("/imports/{import_id}/confirm")
def confirm(import_id: str, db=Depends(get_db), user=Depends(operator)):
    return serialize(imports.confirm(db, user, import_id))


@router.post("/reconciliation")
def reconcile(db=Depends(get_db), user=Depends(operator)):
    return serialize(workflows.reconcile(db, user))


@router.post("/investigations/{case_id}/review")
def review(
    case_id: str,
    body: Decision,
    idempotency_key: Annotated[str, Header(min_length=8, max_length=100)],
    db=Depends(get_db),
    user=Depends(reviewer),
):
    return workflows.review(
        db,
        user,
        case_id,
        body.decision,
        body.note,
        idempotency_key,
        [a.model_dump() for a in body.allocations] if body.allocations is not None else None,
    )


@router.post("/investigations/{case_id}/run")
def run(case_id: str, db=Depends(get_db), user=Depends(operator)):
    if settings.model_mode not in ("baseline", "ollama", "hosted"):
        raise HTTPException(503, "Invalid configured model mode")
    if settings.model_mode == "hosted" and not settings.hosted_enabled:
        raise HTTPException(403, "Hosted inference is not authorised")
    return serialize(
        workflows.enqueue(
            db,
            user,
            case_id,
            settings.model_mode,
            settings.ollama_model if settings.model_mode == "ollama" else settings.hosted_model,
        )
    )


@router.post("/invoices/{invoice_id}/disputes")
def add_dispute(invoice_id: str, body: DisputeInput, db=Depends(get_db), user=Depends(operator)):
    db.scalar(select(Organisation).where(Organisation.id == user.org_id).with_for_update())
    get(db, Invoice, invoice_id, user.org_id, lock=True)
    record = Dispute(org_id=user.org_id, invoice_id=invoice_id, note=body.note, actor_id=user.id)
    db.add(record)
    db.flush()
    audit(db, user, "dispute.opened", record.id, invoice_id=invoice_id)
    db.commit()
    return serialize(record)


@router.post("/disputes/{dispute_id}/resolve")
def resolve_dispute(dispute_id: str, db=Depends(get_db), user=Depends(reviewer)):
    db.scalar(select(Organisation).where(Organisation.id == user.org_id).with_for_update())
    record = get(db, Dispute, dispute_id, user.org_id, lock=True)
    record.status = "resolved"
    audit(db, user, "dispute.resolved", record.id)
    db.commit()
    return serialize(record)


@router.post("/collections/drafts")
def draft(body: DraftInput, db=Depends(get_db), user=Depends(operator)):
    db.scalar(select(Organisation).where(Organisation.id == user.org_id).with_for_update())
    return serialize(workflows.make_draft(db, user, body.invoice_id))


@router.post("/collections/drafts/{draft_id}/review")
def draft_review(draft_id: str, body: DraftDecision, db=Depends(get_db), user=Depends(reviewer)):
    db.scalar(select(Organisation).where(Organisation.id == user.org_id).with_for_update())
    record = get(db, Draft, draft_id, user.org_id, lock=True)
    invoice = get(db, Invoice, record.invoice_id, user.org_id, lock=True)
    if record.status != "draft":
        raise HTTPException(409, "Draft already reviewed")
    if body.decision == "approve" and (disputed(db, invoice) or outstanding(db, invoice) <= 0):
        raise HTTPException(409, "Invoice no longer eligible; generate a new draft")
    record.status = "approved_not_sent" if body.decision == "approve" else "rejected"
    audit(db, user, "collection." + record.status, record.id)
    db.commit()
    return serialize(record)


@router.get("/reports/export")
def export(db=Depends(get_db), user=Depends(current_user)):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["reference", "currency", "amount", "outstanding", "due_date"])
    for invoice in rows(db, Invoice, user.org_id):
        reference = invoice.reference
        if reference.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")):
            reference = "'" + reference
        writer.writerow(
            [
                reference,
                invoice.currency,
                str(invoice.amount),
                str(outstanding(db, invoice)),
                invoice.due_date,
            ]
        )
    return Response(
        output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="receivables.csv"'},
    )


@router.get("/settings")
def config(user=Depends(current_user)):
    import importlib.metadata

    return {
        "mode": settings.model_mode,
        "model": settings.ollama_model
        if settings.model_mode == "ollama"
        else settings.hosted_model or None,
        "crewai_version": importlib.metadata.version("crewai"),
        "environment": settings.app_env,
        "demo_enabled": settings.demo_enabled,
        "allocation_policy": "human_review_all",
        "communications": "disabled",
        "currencies": ["ZAR", "USD", "EUR", "GBP", "JPY", "KWD"],
        "workflow_store": "PostgreSQL",
        "hosted_enabled": settings.hosted_enabled,
        "telemetry": "disabled",
        "evaluation": "Run python -m app.evaluations.runner; see docs/testing/results.md",
    }


@router.get("/{resource}")
def listing(
    resource: str,
    q: str = Query("", max_length=200),
    status: str = "",
    currency: str = "",
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    sort: str = "",
    direction: str = "asc",
    db=Depends(get_db),
    user=Depends(current_user),
):
    model = MODELS.get(resource)
    if not model:
        raise HTTPException(404, "Resource not found")
    records = [present(db, r) for r in rows(db, model, user.org_id)]
    records = [
        r
        for r in records
        if (not q or q.casefold() in json.dumps(r).casefold())
        and (not status or r.get("status") == status)
        and (not currency or r.get("currency") == currency)
    ]
    if sort and records and sort in records[0]:
        records.sort(key=lambda r: str(r.get(sort) or ""), reverse=direction == "desc")
    elif records and "created_at" in records[0]:
        records.sort(key=lambda r: r["created_at"], reverse=True)
    return {
        "items": records[(page - 1) * page_size : page * page_size],
        "total": len(records),
        "page": page,
        "page_size": page_size,
    }


@router.get("/{resource}/{record_id}")
def detail(resource: str, record_id: str, db=Depends(get_db), user=Depends(current_user)):
    model = MODELS.get(resource)
    if not model:
        raise HTTPException(404, "Resource not found")
    record = get(db, model, record_id, user.org_id)
    result = present(db, record)
    if model in (Invoice, Transaction, Customer, Investigation):
        for name, child in (
            ("allocations", Allocation),
            ("reviews", Review),
            ("disputes", Dispute),
            ("drafts", Draft),
            ("executions", Execution),
            ("invoices", Invoice),
            ("transactions", Transaction),
        ):
            foreign_key = {
                Invoice: "invoice_id",
                Transaction: "transaction_id",
                Customer: "customer_id",
                Investigation: "investigation_id",
            }[model]
            if hasattr(child, foreign_key):
                result[name] = [
                    present(db, r)
                    for r in rows(db, child, user.org_id)
                    if getattr(r, foreign_key) == record.id
                ]
    return result


@router.post("/investigations/{case_id}/collections-run")
def collection_run(case_id: str, db=Depends(get_db), user=Depends(operator)):
    if settings.model_mode == "hosted" and not settings.hosted_enabled:
        raise HTTPException(403, "Hosted inference is not authorised")
    return serialize(
        workflows.enqueue(
            db,
            user,
            case_id,
            settings.model_mode,
            settings.ollama_model if settings.model_mode == "ollama" else settings.hosted_model,
            purpose="collections",
        )
    )


@router.get("/integrations/model-health")
def model_health(user=Depends(current_user)):
    from app.providers.models import health

    try:
        return health()
    except Exception:
        raise HTTPException(503, "Model unavailable or required capabilities absent") from None
