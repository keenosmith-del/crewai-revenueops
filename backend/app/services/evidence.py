from app.models.entities import Customer, Dispute, Investigation, Invoice, Transaction
from app.repositories.records import get, rows
from app.services.ledger import available, disputed, outstanding
from app.services.reporting import serialize


def snapshot(db, org, case_id):
    case = get(db, Investigation, case_id, org)
    tx = get(db, Transaction, case.transaction_id, org)
    invoices = [
        i
        for i in rows(db, Invoice, org)
        if i.currency == tx.currency
        and (not tx.customer_id or i.customer_id == tx.customer_id)
        and outstanding(db, i) > 0
    ][:50]
    records = {
        f"transaction:{tx.id}": {
            k: str(v)
            for k, v in serialize(tx).items()
            if k
            in (
                "id",
                "reference",
                "amount",
                "currency",
                "payment_date",
                "customer_id",
                "duplicate_of",
            )
        }
    }
    records[f"transaction:{tx.id}"]["available"] = str(available(db, tx))
    for invoice in invoices:
        record = {
            k: str(v)
            for k, v in serialize(invoice).items()
            if k in ("id", "reference", "amount", "currency", "due_date", "customer_id")
        }
        record.update(
            outstanding=str(outstanding(db, invoice)), disputed=str(disputed(db, invoice))
        )
        records[f"invoice:{invoice.id}"] = record
        for dispute in rows(db, Dispute, org):
            if dispute.invoice_id == invoice.id:
                records[f"dispute:{dispute.id}"] = {
                    "invoice_id": invoice.id,
                    "note": dispute.note,
                    "status": dispute.status,
                }
    if tx.customer_id:
        customer = get(db, Customer, tx.customer_id, org)
        records[f"customer:{customer.id}"] = {
            "id": customer.id,
            "name": customer.name,
            "account": customer.account,
        }
    return {
        "investigation_id": case.id,
        "transaction_id": tx.id,
        "classification": case.classification,
        "currency": tx.currency,
        "records": records,
    }
