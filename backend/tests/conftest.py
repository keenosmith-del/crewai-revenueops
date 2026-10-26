import os
from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app
from app.models.entities import Customer, Invoice, Organisation, Transaction, User
from app.security.auth import token


@pytest.fixture
def db():
    url = os.getenv("TEST_DATABASE_URL", "sqlite://")
    engine = create_engine(
        url,
        **(
            {"poolclass": StaticPool, "connect_args": {"check_same_thread": False}}
            if url == "sqlite://"
            else {}
        ),
    )
    # Only the explicit dedicated TEST_DATABASE_URL is ever dropped.
    if url != "sqlite://" and not url.rsplit("/", 1)[-1].endswith("_test"):
        raise RuntimeError("Test database name must end in _test")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with sessionmaker(engine, expire_on_commit=False)() as session:
        yield session
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def user(db):
    db.add(Organisation(id="org", name="Synthetic", synthetic=True))
    db.flush()
    user = User(
        id="reviewer",
        org_id="org",
        email="test@example.com",
        password_hash="unused",
        role="reviewer",
    )
    db.add(user)
    db.add(
        Customer(
            id="customer", org_id="org", account="SYN", name="Synthetic", email="a@example.com"
        )
    )
    db.flush()
    db.add(
        Invoice(
            id="invoice",
            org_id="org",
            customer_id="customer",
            reference="INV-001",
            amount=Decimal("100"),
            currency="ZAR",
            issue_date=date(2026, 1, 1),
            due_date=date(2026, 2, 1),
        )
    )
    db.add(
        Transaction(
            id="tx",
            org_id="org",
            customer_id="customer",
            source_id="TX-001",
            reference="INV-001",
            amount=Decimal("100"),
            currency="ZAR",
            payment_date=date(2026, 2, 2),
        )
    )
    db.commit()
    return user


@pytest.fixture
def client(db, user):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        c.headers["Authorization"] = "Bearer " + token(user)
        yield c
    app.dependency_overrides.clear()
