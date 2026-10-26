from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.models.entities import Allocation, Investigation, Transaction
from app.services.workflows import reconcile, review


def test_postgres_concurrent_payments_cannot_overallocate(db, user):
    if db.bind.dialect.name != "postgresql":
        pytest.skip("Requires real PostgreSQL row locks")
    tx = db.get(Transaction, "tx")
    db.add(
        Transaction(
            id="tx2",
            org_id="org",
            customer_id="customer",
            source_id="TX-002",
            reference="INV-001",
            amount=Decimal("100"),
            currency="ZAR",
            payment_date=tx.payment_date,
        )
    )
    db.commit()
    reconcile(db, user)
    ids = list(db.scalars(select(Investigation.id)))
    actor = SimpleNamespace(id=user.id, org_id=user.org_id)
    factory = sessionmaker(db.bind, expire_on_commit=False)

    def approve(case):
        with factory() as session:
            try:
                review(
                    session,
                    actor,
                    case,
                    "approve",
                    "Verified concurrent receipt",
                    "concurrent-" + case,
                )
                return "approved"
            except HTTPException as error:
                session.rollback()
                return error.status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(approve, ids))
    assert sorted(map(str, results)) == ["409", "approved"]
    db.expire_all()
    assert sum(a.amount for a in db.scalars(select(Allocation))) == 100
