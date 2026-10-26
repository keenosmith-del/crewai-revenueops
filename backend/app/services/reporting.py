from datetime import date
from decimal import Decimal

from sqlalchemy.inspection import inspect

from app.models.entities import (
    Allocation,
    Audit,
    Customer,
    Dispute,
    Execution,
    Investigation,
    Invoice,
    Transaction,
)
from app.repositories.records import rows
from app.services.ledger import available, disputed, outstanding


def serialize(record):
    result = {}
    for column in inspect(record).mapper.column_attrs:
        key = column.key
        if key in ("password_hash", "lease_token"):
            continue
        value = getattr(record, key)
        result[key] = (
            str(value)
            if isinstance(value, Decimal)
            else value.isoformat()
            if hasattr(value, "isoformat")
            else value
        )
    return result


def present(db, record):
    result = serialize(record)
    if isinstance(record, Invoice):
        result.update(outstanding=str(outstanding(db, record)), disputed=disputed(db, record))
        result["status"] = (
            "disputed"
            if result["disputed"]
            else "paid"
            if Decimal(result["outstanding"]) == 0
            else "overdue"
            if record.due_date < date.today()
            else "open"
        )
    if isinstance(record, Transaction):
        result.update(
            unallocated=str(available(db, record)),
            status="reversal"
            if record.amount < 0
            else "duplicate"
            if record.duplicate_of
            else "allocated"
            if available(db, record) == 0
            else "unallocated",
        )
    return result


def report(db, org, currency="ZAR", start=None, end=None):
    invoices = [
        i
        for i in rows(db, Invoice, org)
        if i.currency == currency
        and (not start or i.issue_date >= start)
        and (not end or i.issue_date <= end)
    ]
    txs = [
        t
        for t in rows(db, Transaction, org)
        if t.currency == currency
        and (not start or t.payment_date >= start)
        and (not end or t.payment_date <= end)
    ]
    executions = rows(db, Execution, org)
    aging = {
        "current": Decimal(0),
        "1–30 days": Decimal(0),
        "31–60 days": Decimal(0),
        "61–90 days": Decimal(0),
        "90+ days": Decimal(0),
    }
    for i in invoices:
        days = (date.today() - i.due_date).days
        bucket = (
            "current"
            if days <= 0
            else "1–30 days"
            if days <= 30
            else "31–60 days"
            if days <= 60
            else "61–90 days"
            if days <= 90
            else "90+ days"
        )
        aging[bucket] += outstanding(db, i)
    return {
        "currency": currency,
        "as_of": date.today().isoformat(),
        "total_invoiced": str(sum((i.amount for i in invoices), Decimal(0))),
        "total_received": str(sum((t.amount for t in txs if t.amount > 0), Decimal(0))),
        "outstanding": str(sum((outstanding(db, i) for i in invoices), Decimal(0))),
        "unallocated_amount": str(sum((available(db, t) for t in txs if t.amount > 0), Decimal(0))),
        "unallocated_transactions": sum(available(db, t) > 0 for t in txs),
        "overdue_invoices": sum(
            outstanding(db, i) > 0 and i.due_date < date.today() for i in invoices
        ),
        "active_disputes": sum(d.status == "open" for d in rows(db, Dispute, org)),
        "pending_investigations": sum(
            c.status not in ("allocated", "rejected") for c in rows(db, Investigation, org)
        ),
        "completed_reconciliations": sum(
            c.status == "allocated" for c in rows(db, Investigation, org)
        ),
        "customers": len(rows(db, Customer, org)),
        "aging": {k: str(v) for k, v in aging.items()},
        "agent_status": {
            state: sum(e.status == state for e in executions)
            for state in ("queued", "running", "completed", "failed", "not_executed")
        },
        "average_execution_ms": sum(e.duration_ms or 0 for e in executions)
        // max(1, sum(e.duration_ms is not None for e in executions)),
        "recent_activity": [
            serialize(a)
            for a in sorted(rows(db, Audit, org), key=lambda a: a.created_at, reverse=True)[:10]
        ],
        "allocations": len(rows(db, Allocation, org)),
    }
