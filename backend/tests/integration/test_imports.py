import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.models.entities import Invoice
from app.services.imports import confirm, preview

CSV = b"reference,account,amount,currency,issue_date,due_date\nINV-002,SYN,100.00,ZAR,2026-01-01,2026-02-01\n"


def test_preview_confirm_idempotent(db, user):
    p = preview(db, user, "invoices", CSV, "test.csv", {})
    assert not p.errors
    assert preview(db, user, "invoices", CSV, "again.csv", {}).id == p.id
    confirm(db, user, p.id)
    confirm(db, user, p.id)
    assert len(list(db.scalars(select(Invoice)))) == 2


def test_invalid_atomic(db, user):
    p = preview(
        db, user, "invoices", CSV + b"INV-003,SYN,1.001,ZAR,2026-01-01,2026-02-01\n", "bad.csv", {}
    )
    assert len(p.errors) == 1
    with pytest.raises(HTTPException):
        confirm(db, user, p.id)
    assert len(list(db.scalars(select(Invoice)))) == 1
