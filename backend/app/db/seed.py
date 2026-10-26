"""Reproducible synthetic business; safe to rerun, never active in production."""

import csv
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.entities import Customer, Dispute, Invoice, Organisation, Transaction, User
from app.security.auth import passwords


def seed(db, *, org_id="synthetic-revenueops", count=150):
    if not settings.demo_enabled or settings.app_env == "production":
        raise RuntimeError("Synthetic seeding disabled")
    if db.get(Organisation, org_id):
        return
    org = Organisation(id=org_id, name="Northstar Studio · Synthetic", synthetic=True)
    db.add(org)
    db.flush()
    for role in ("admin", "reviewer", "analyst", "viewer"):
        db.add(
            User(
                id=f"{org_id}-{role}",
                org_id=org_id,
                email=f"{role}@revenueops.example",
                role=role,
                password_hash=passwords.hash("Demo-finance-2026!"),
            )
        )
    db.flush()
    customers = []
    for n, name in enumerate(
        [
            "Acorn Design",
            "Atlas Paper",
            "Cedar Systems",
            "Harbour Works",
            "Lumen Studio",
            "Orchard Labs",
            "Pebble Supply",
            "Sable Group",
            "Willow Goods",
            "Juniper Digital",
        ]
    ):
        customer = Customer(
            id=f"{org_id}-c{n}",
            org_id=org_id,
            name=name,
            account=f"SYN-{n:03}",
            email=f"accounts{n}@customer.example",
        )
        db.add(customer)
        customers.append(customer)
    db.flush()
    base = date(2026, 10, 26)
    invoices = []
    for n in range(count):
        invoice = Invoice(
            id=f"{org_id}-i{n}",
            org_id=org_id,
            customer_id=customers[n % 10].id,
            reference=f"SYN-INV-{n + 1:04}",
            amount=Decimal(1000 + n * 37),
            currency="ZAR",
            issue_date=base - timedelta(days=130 - n % 110),
            due_date=base - timedelta(days=100 - n % 110),
        )
        invoices.append(invoice)
        db.add(invoice)
    db.flush()
    for n in range(min(120, count)):
        invoice = invoices[n]
        amount, reference = invoice.amount, invoice.reference
        if 60 <= n < 70:
            amount /= 2
        elif 70 <= n < 80:
            amount += 100
        elif 80 <= n < 90:
            reference = ""
        elif 90 <= n < 100:
            reference = "SYN incorrect reference"
        elif 100 <= n < 105:
            amount = -amount
        elif 105 <= n < 110:
            reference = f"{invoice.reference} {invoices[n + 10].reference}"
            amount += invoices[n + 10].amount
        elif 110 <= n < 115:
            reference = "Unallocated deposit"
            amount = Decimal("123.45")
        tx = Transaction(
            id=f"{org_id}-t{n}",
            org_id=org_id,
            customer_id=invoice.customer_id if n < 110 else None,
            source_id=f"SYN-BANK-{n:04}",
            reference=reference,
            amount=amount,
            currency="ZAR",
            payment_date=base - timedelta(days=n % 45),
        )
        if 115 <= n < 120:
            source = invoices[n - 115]
            tx.reference, tx.amount, tx.customer_id = (
                source.reference,
                source.amount,
                source.customer_id,
            )
            tx.duplicate_of = f"{org_id}-t{n - 115}"
        db.add(tx)
    db.flush()
    for n in (12, 32, 52, 72):
        if n < count:
            db.add(
                Dispute(
                    org_id=org_id,
                    invoice_id=invoices[n].id,
                    note="Synthetic customer requests confirmation of service delivery.",
                    actor_id=f"{org_id}-reviewer",
                )
            )
    db.commit()


def export_templates(db):
    root = Path(__file__).resolve().parents[3] / "data" / "synthetic"
    root.mkdir(parents=True, exist_ok=True)
    accounts = {c.id: c.account for c in db.scalars(select(Customer))}
    for name, model, fields in [
        (
            "invoices",
            Invoice,
            ["reference", "account", "amount", "currency", "issue_date", "due_date"],
        ),
        (
            "transactions",
            Transaction,
            ["source_id", "account", "reference", "amount", "currency", "payment_date"],
        ),
    ]:
        with (root / f"{name}.csv").open("w") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            for item in db.scalars(select(model).where(model.org_id == "synthetic-revenueops")):
                writer.writerow(
                    {
                        k: accounts.get(item.customer_id, "")
                        if k == "account"
                        else getattr(item, k)
                        for k in fields
                    }
                )


if __name__ == "__main__":
    with SessionLocal() as session:
        seed(session)
        export_templates(session)
    print("Synthetic records ready; reviewer@revenueops.example / Demo-finance-2026!")
