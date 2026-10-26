import pytest

from app.core.config import Settings
from app.models.entities import Transaction


def test_production_fails_closed():
    with pytest.raises(ValueError):
        Settings(app_env="production", demo_enabled=True).validate_runtime()
    with pytest.raises(ValueError):
        Settings(app_env="production", demo_enabled=False, jwt_secret="short").validate_runtime()


def test_formula_export_and_account_verification(client, db, user):
    from app.models.entities import Invoice

    invoice = db.get(Invoice, "invoice")
    invoice.reference = '=HYPERLINK("evil")'
    db.commit()
    response = client.get("/api/reports/export")
    assert response.status_code == 200 and "'=HYPERLINK" in response.text
    tx = db.get(Transaction, "tx")
    tx.customer_id = None
    db.commit()
    result = client.post(
        "/api/transactions/tx/verify-account",
        json={"customer_id": "customer", "note": "Verified against customer account record"},
    )
    assert result.status_code == 200
    assert result.json()["customer_id"] == "customer"


def test_customer_provisioning_contract(client):
    response = client.post(
        "/api/customers",
        json={"name": "Synthetic New", "account": "NEW-01", "email": "new@example.com"},
    )
    assert response.status_code == 200
    assert client.get("/api/customers/" + response.json()["id"]).status_code == 200
