from decimal import Decimal

from sqlalchemy import func, select

from app.models.entities import Allocation, Audit, Dispute


def allocated(db, org, *, invoice_id=None, transaction_id=None):
    query = select(func.coalesce(func.sum(Allocation.amount), 0)).where(Allocation.org_id == org)
    if invoice_id:
        query = query.where(Allocation.invoice_id == invoice_id)
    if transaction_id:
        query = query.where(Allocation.transaction_id == transaction_id)
    return Decimal(db.scalar(query))


def outstanding(db, invoice):
    return invoice.amount - allocated(db, invoice.org_id, invoice_id=invoice.id)


def available(db, tx):
    return tx.amount - allocated(db, tx.org_id, transaction_id=tx.id)


def disputed(db, invoice):
    return (
        db.scalar(
            select(Dispute.id).where(
                Dispute.org_id == invoice.org_id,
                Dispute.invoice_id == invoice.id,
                Dispute.status == "open",
            )
        )
        is not None
    )


def audit(db, user, action, record_id, **detail):
    db.add(
        Audit(
            org_id=user.org_id, actor_id=user.id, action=action, record_id=record_id, detail=detail
        )
    )
