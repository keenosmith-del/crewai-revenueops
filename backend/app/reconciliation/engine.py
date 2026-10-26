import re
from itertools import combinations

from app.models.entities import Invoice
from app.repositories.records import rows
from app.services.ledger import available, disputed, outstanding


def classify(db, tx):
    if tx.amount < 0:
        return "reversal", []
    if tx.duplicate_of:
        return "duplicate", []
    remaining = available(db, tx)
    if remaining <= 0:
        return "allocated", []
    invoices = [
        i
        for i in rows(db, Invoice, tx.org_id)
        if i.currency == tx.currency
        and (not tx.customer_id or i.customer_id == tx.customer_id)
        and outstanding(db, i) > 0
    ]
    references = [
        i
        for i in invoices
        if re.search(r"(?<![\w-])" + re.escape(i.reference) + r"(?![\w-])", tx.reference, re.I)
    ]
    if references:
        if any(disputed(db, i) for i in references):
            return "disputed", []
        total = sum(outstanding(db, i) for i in references)
        if len(references) > 1:
            return (
                ("combined", [(i, outstanding(db, i)) for i in references])
                if total == remaining
                else ("ambiguous", [])
            )
        invoice = references[0]
        balance = outstanding(db, invoice)
        return (
            "exact" if remaining == balance else "partial" if remaining < balance else "overpayment"
        ), [(invoice, min(remaining, balance))]
    exact = [i for i in invoices if outstanding(db, i) == remaining and not disputed(db, i)]
    if len(exact) == 1 and tx.customer_id:
        return "amount_customer", [(exact[0], remaining)]
    if tx.customer_id and len(invoices) <= 18:
        groups = [
            g
            for size in (2, 3)
            for g in combinations(invoices, size)
            if not any(disputed(db, i) for i in g)
            and sum(outstanding(db, i) for i in g) == remaining
        ]
        if len(groups) == 1:
            return "combined_candidate", [(i, outstanding(db, i)) for i in groups[0]]
    return ("ambiguous" if exact else "unmatched"), []
