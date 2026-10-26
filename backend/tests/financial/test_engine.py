from decimal import Decimal

from app.models.entities import Invoice, Transaction
from app.reconciliation.engine import classify


def test_exact_and_partial(db, user):
    tx = db.get(Transaction, "tx")
    assert classify(db, tx)[0] == "exact"
    tx.amount = Decimal("50")
    assert classify(db, tx)[0] == "partial"
    tx.amount = Decimal("150")
    assert classify(db, tx)[0] == "overpayment"


def test_reference_boundary(db, user):
    tx = db.get(Transaction, "tx")
    tx.reference = "INV-0011"
    tx.customer_id = None
    assert classify(db, tx)[0] == "ambiguous"


def test_reversal_duplicate(db, user):
    tx = db.get(Transaction, "tx")
    tx.amount = Decimal("-1")
    assert classify(db, tx) == ("reversal", [])
    tx.amount = Decimal("100")
    tx.duplicate_of = "tx"
    assert classify(db, tx) == ("duplicate", [])


def test_combined(db, user):
    invoice = db.get(Invoice, "invoice")
    second = Invoice(
        id="second",
        org_id="org",
        customer_id="customer",
        reference="INV-002",
        amount=Decimal("50"),
        currency="ZAR",
        issue_date=invoice.issue_date,
        due_date=invoice.due_date,
    )
    db.add(second)
    db.flush()
    tx = db.get(Transaction, "tx")
    tx.reference = "INV-001 INV-002"
    tx.amount = Decimal("150")
    kind, parts = classify(db, tx)
    assert kind == "combined" and sum(p[1] for p in parts) == 150
