import csv
import hashlib
import io
from datetime import date

from fastapi import HTTPException
from sqlalchemy import select

from app.accounting.money import money
from app.models.entities import Customer, Import, Invoice, Transaction
from app.repositories.records import get, rows
from app.services.ledger import audit

REQUIRED = {
    "invoices": ["reference", "account", "amount", "currency", "issue_date", "due_date"],
    "transactions": ["source_id", "account", "reference", "amount", "currency", "payment_date"],
}


def preview(db, user, kind, content, filename, mapping):
    if kind not in REQUIRED or len(content) > 2_000_000 or b"\0" in content:
        raise HTTPException(422, "Unsupported CSV or size exceeds 2 MB")
    digest = hashlib.sha256(content + str(sorted(mapping.items())).encode()).hexdigest()
    previous = db.scalar(
        select(Import).where(
            Import.org_id == user.org_id, Import.kind == kind, Import.source_hash == digest
        )
    )
    if previous:
        return previous
    try:
        reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError("Missing or duplicate CSV headers")
        source_columns = [mapping.get(k, k) for k in REQUIRED[kind]]
        if not set(source_columns).issubset(reader.fieldnames):
            raise ValueError(f"Required columns: {', '.join(REQUIRED[kind])}")
        valid, errors, seen = [], [], set()
        customers = {c.account: c.id for c in rows(db, Customer, user.org_id)}
        model = Invoice if kind == "invoices" else Transaction
        key = "reference" if kind == "invoices" else "source_id"
        existing = {getattr(r, key) for r in rows(db, model, user.org_id)}
        for number, source in enumerate(reader, 2):
            if number > 5001:
                raise ValueError("Maximum 5000 rows")
            try:
                if None in source:
                    raise ValueError("Malformed row")
                row = {k: (source.get(mapping.get(k, k)) or "").strip() for k in REQUIRED[kind]}
                if any(len(v) > 200 for v in row.values()):
                    raise ValueError("Field too long")
                if not row[key]:
                    raise ValueError("Missing record identifier")
                row["amount"] = str(money(row["amount"], row["currency"]))
                if money(row["amount"], row["currency"]) == 0 or (
                    kind == "invoices" and money(row["amount"], row["currency"]) < 0
                ):
                    raise ValueError("Invalid amount sign")
                for field in (
                    ("issue_date", "due_date") if kind == "invoices" else ("payment_date",)
                ):
                    date.fromisoformat(row[field])
                if kind == "invoices" and row["due_date"] < row["issue_date"]:
                    raise ValueError("Due date precedes issue date")
                if row["account"] and row["account"] not in customers:
                    raise ValueError("Unknown customer account")
                if kind == "invoices" and not row["account"]:
                    raise ValueError("Invoice requires customer")
                if row[key] in seen or row[key] in existing:
                    raise ValueError("Duplicate record identifier")
                seen.add(row[key])
                row["customer_id"] = customers.get(row.pop("account"))
                valid.append(row)
            except ValueError as exc:
                errors.append({"row": number, "message": str(exc)})
        if not valid and not errors:
            raise ValueError("CSV is empty")
    except (UnicodeError, ValueError, csv.Error) as exc:
        raise HTTPException(422, str(exc)) from exc
    record = Import(
        org_id=user.org_id,
        kind=kind,
        filename=filename[:160],
        source_hash=digest,
        rows=valid,
        errors=errors,
    )
    db.add(record)
    db.flush()
    audit(db, user, "import.preview", record.id, valid=len(valid), errors=len(errors))
    db.commit()
    return record


def confirm(db, user, import_id):
    record = get(db, Import, import_id, user.org_id, lock=True)
    if record.status == "confirmed":
        return record
    if record.errors:
        raise HTTPException(409, "Fix row errors before confirming the entire import")
    model = Invoice if record.kind == "invoices" else Transaction
    key = "reference" if model is Invoice else "source_id"
    # Serialise confirmations per organisation to prevent concurrent duplicate imports.
    from app.models.entities import Organisation

    db.scalar(select(Organisation).where(Organisation.id == user.org_id).with_for_update())
    for item in record.rows:
        if db.scalar(
            select(model.id).where(model.org_id == user.org_id, getattr(model, key) == item[key])
        ):
            raise HTTPException(409, "Record imported since preview; create a fresh source")
        values = dict(item)
        values["amount"] = money(values["amount"], values["currency"])
        for field in ("issue_date", "due_date") if model is Invoice else ("payment_date",):
            values[field] = date.fromisoformat(values[field])
        if model is Transaction:
            duplicate = db.scalar(
                select(Transaction).where(
                    Transaction.org_id == user.org_id,
                    Transaction.reference == values["reference"],
                    Transaction.amount == values["amount"],
                    Transaction.currency == values["currency"],
                    Transaction.payment_date == values["payment_date"],
                    Transaction.customer_id == values["customer_id"],
                )
            )
            values["duplicate_of"] = duplicate.id if duplicate else None
        db.add(model(org_id=user.org_id, import_id=record.id, **values))
        db.flush()
    record.status = "confirmed"
    audit(db, user, "import.confirmed", record.id, count=len(record.rows))
    db.commit()
    return record
