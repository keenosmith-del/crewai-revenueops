from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.models.entities import Allocation, Dispute, Investigation, Invoice, Transaction
from app.services.ledger import outstanding
from app.services.workflows import make_draft, reconcile, review


def get_case(db, user):
    reconcile(db, user)
    return db.scalar(select(Investigation))


def test_approval_replay_and_balance(db, user):
    case = get_case(db, user)
    result = review(db, user, case.id, "approve", "Verified receipt", "same-key-001")
    assert review(db, user, case.id, "approve", "Verified receipt", "same-key-001") == result
    assert outstanding(db, db.get(Invoice, "invoice")) == 0
    assert len(list(db.scalars(select(Allocation)))) == 1
    with pytest.raises(HTTPException):
        review(db, user, case.id, "reject", "Changed request", "same-key-001")


def test_rejection_never_changes_money(db, user):
    case = get_case(db, user)
    review(db, user, case.id, "reject", "Need evidence", "reject-key-001")
    assert outstanding(db, db.get(Invoice, "invoice")) == 100


@pytest.mark.parametrize(
    "mutation",
    [
        "overallocate",
        "currency",
        "customer",
        "dispute",
        "duplicate",
        "negative",
        "duplicate_invoice",
    ],
)
def test_financial_guardrails(db, user, mutation):
    case = get_case(db, user)
    items = [{"invoice_id": "invoice", "amount": "100"}]
    tx = db.get(Transaction, "tx")
    if mutation == "overallocate":
        items[0]["amount"] = "101"
    if mutation == "currency":
        tx.currency = "USD"
    if mutation == "customer":
        tx.customer_id = None
    if mutation == "dispute":
        db.add(Dispute(org_id="org", invoice_id="invoice", note="Disputed", actor_id=user.id))
    if mutation == "duplicate":
        tx.duplicate_of = tx.id
    if mutation == "negative":
        items[0]["amount"] = "-1"
    if mutation == "duplicate_invoice":
        items = items * 2
    db.flush()
    with pytest.raises(HTTPException):
        review(db, user, case.id, "approve", "Reviewed proposal", "guard-key-001", items)
    assert not list(db.scalars(select(Allocation)))


def test_reconcile_repeat_and_draft(db, user):
    get_case(db, user)
    reconcile(db, user)
    assert len(list(db.scalars(select(Investigation)))) == 1
    draft = make_draft(db, user, "invoice")
    assert draft.status == "draft" and "100" in draft.body


def test_partial_allocation_then_stale_proposal(db, user):
    case = get_case(db, user)
    review(
        db,
        user,
        case.id,
        "approve",
        "Partial approved",
        "partial-key-001",
        [{"invoice_id": "invoice", "amount": "40"}],
    )
    assert outstanding(db, db.get(Invoice, "invoice")) == Decimal("60")
    review(
        db,
        user,
        case.id,
        "approve",
        "Remaining approved",
        "partial-key-002",
        [{"invoice_id": "invoice", "amount": "60"}],
    )
    assert outstanding(db, db.get(Invoice, "invoice")) == 0
