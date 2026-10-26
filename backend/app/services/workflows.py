import hashlib
import json
from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select

from app.accounting.money import money
from app.models.entities import (
    Allocation,
    Batch,
    Draft,
    Execution,
    Idempotency,
    Investigation,
    Invoice,
    Organisation,
    Review,
    Transaction,
)
from app.reconciliation.engine import classify
from app.repositories.records import get, rows
from app.services.ledger import audit, available, disputed, outstanding


def reconcile(db, user):
    db.scalar(select(Organisation).where(Organisation.id == user.org_id).with_for_update())
    batch = Batch(org_id=user.org_id)
    db.add(batch)
    db.flush()
    summary = {}
    for tx in sorted(rows(db, Transaction, user.org_id), key=lambda r: r.id):
        if available(db, tx) == 0:
            continue
        case = db.scalar(
            select(Investigation).where(
                Investigation.org_id == user.org_id, Investigation.transaction_id == tx.id
            )
        )
        if case:
            continue
        category, matches = classify(db, tx)
        case = Investigation(
            org_id=user.org_id,
            transaction_id=tx.id,
            batch_id=batch.id,
            classification=category,
            status="human_review",
            proposal={
                "allocations": [{"invoice_id": i.id, "amount": str(a)} for i, a in matches],
                "currency": tx.currency,
                "source": "deterministic",
            },
            explanation=f"{category.replace('_', ' ')}; finance review required",
        )
        db.add(case)
        summary[category] = summary.get(category, 0) + 1
    batch.summary = summary
    audit(db, user, "reconciliation.completed", batch.id, summary=summary)
    db.commit()
    return batch


def validate_allocations(db, case, items, *, lock=False):
    tx = get(db, Transaction, case.transaction_id, case.org_id, lock=lock)
    if tx.amount <= 0 or tx.duplicate_of:
        raise HTTPException(409, "Reversal or suspected duplicate requires separate investigation")
    if not items or len(items) > 30:
        raise HTTPException(422, "Propose between 1 and 30 allocations")
    if len({a["invoice_id"] for a in items}) != len(items):
        raise HTTPException(422, "Duplicate invoice in proposal")
    total, validated = Decimal(0), []
    for item in sorted(items, key=lambda i: i["invoice_id"]):
        invoice = get(db, Invoice, item["invoice_id"], case.org_id, lock=lock)
        amount = money(item["amount"], tx.currency)
        if invoice.currency != tx.currency:
            raise HTTPException(409, "Cross-currency allocation unsupported")
        if not tx.customer_id or invoice.customer_id != tx.customer_id:
            raise HTTPException(
                409, "Verified matching customer account required before allocation"
            )
        if disputed(db, invoice):
            raise HTTPException(409, "Resolve invoice dispute before allocating")
        if amount <= 0 or amount > outstanding(db, invoice):
            raise HTTPException(409, "Amount exceeds invoice outstanding or is not positive")
        total += amount
        validated.append((invoice, amount))
    if total > available(db, tx):
        raise HTTPException(409, "Allocations exceed available payment")
    return tx, validated


def review(db, user, case_id, decision, note, key, allocations=None):
    fingerprint = hashlib.sha256(
        json.dumps([case_id, decision, note, allocations], sort_keys=True).encode()
    ).hexdigest()
    # Lock organisation first, then case/transaction/invoices, consistently across all writes.
    db.scalar(select(Organisation).where(Organisation.id == user.org_id).with_for_update())
    previous = db.scalar(
        select(Idempotency).where(Idempotency.org_id == user.org_id, Idempotency.key == key)
    )
    if previous:
        if previous.fingerprint != fingerprint:
            raise HTTPException(409, "Idempotency key reused for a different request")
        return previous.result
    case = get(db, Investigation, case_id, user.org_id, lock=True)
    if case.status not in ("human_review", "partially_allocated", "rejected", "needs_information"):
        raise HTTPException(409, "Case cannot be reviewed in its current state")
    old = case.status
    if decision == "approve":
        items = allocations if allocations is not None else case.proposal.get("allocations", [])
        tx, validated = validate_allocations(db, case, items, lock=True)
        for invoice, amount in validated:
            db.add(
                Allocation(
                    org_id=user.org_id,
                    transaction_id=tx.id,
                    invoice_id=invoice.id,
                    investigation_id=case.id,
                    amount=amount,
                    actor_id=user.id,
                )
            )
        db.flush()
        case.status = "allocated" if available(db, tx) == 0 else "partially_allocated"
    elif decision == "reject":
        case.status = "rejected"
    elif decision == "request_information":
        case.status = "needs_information"
    else:
        raise HTTPException(422, "Invalid review decision")
    db.add(
        Review(
            org_id=user.org_id,
            investigation_id=case.id,
            actor_id=user.id,
            decision=decision,
            note=note,
        )
    )
    audit(db, user, "review." + decision, case.id, previous=old, new=case.status, note=note)
    result = {"id": case.id, "status": case.status}
    db.add(Idempotency(org_id=user.org_id, key=key, fingerprint=fingerprint, result=result))
    db.commit()
    return result


def enqueue(db, user, case_id, mode, model):
    case = get(db, Investigation, case_id, user.org_id, lock=True)
    if case.status not in ("human_review", "needs_information", "rejected", "failed"):
        raise HTTPException(409, "Case already running or terminal")
    execution = Execution(
        org_id=user.org_id,
        investigation_id=case.id,
        mode=mode,
        model=model,
        status="not_executed" if mode == "baseline" else "queued",
        stage="not_executed" if mode == "baseline" else "queued",
        error="No model execution in baseline mode" if mode == "baseline" else None,
    )
    db.add(execution)
    if mode != "baseline":
        case.status = "queued"
    db.flush()
    audit(db, user, "investigation.requested", execution.id, mode=mode)
    db.commit()
    return execution


def make_draft(db, user, invoice_id):
    invoice = get(db, Invoice, invoice_id, user.org_id, lock=True)
    if invoice.due_date >= date.today() or outstanding(db, invoice) <= 0 or disputed(db, invoice):
        raise HTTPException(409, "Only undisputed overdue balances are eligible")
    balance = outstanding(db, invoice)
    draft = Draft(
        org_id=user.org_id,
        invoice_id=invoice.id,
        actor_id=user.id,
        body=f"Hello, our records show invoice {invoice.reference}, due {invoice.due_date}, has an outstanding balance of {balance} {invoice.currency}. Please let us know if payment has already been made or if you need supporting information. Thank you.",
    )
    db.add(draft)
    db.flush()
    audit(
        db,
        user,
        "collection.drafted",
        draft.id,
        invoice_id=invoice.id,
        source="deterministic_template",
    )
    db.commit()
    return draft
