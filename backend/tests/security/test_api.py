import pytest
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app
from app.models.entities import Customer, Organisation
from app.security.auth import passwords, token


@pytest.fixture
def client(db, user):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        c.headers["Authorization"] = "Bearer " + token(user)
        yield c
    app.dependency_overrides.clear()


def test_authentication_required():
    with TestClient(app) as c:
        assert c.get("/api/invoices").status_code == 401


def test_organisation_isolation(client, db, user):
    db.add(Organisation(id="other", name="Other", synthetic=True))
    db.flush()
    db.add(
        Customer(
            id="other-customer",
            org_id="other",
            account="OTHER",
            name="Other",
            email="other@example.com",
        )
    )
    db.commit()
    assert client.get("/api/customers/other-customer").status_code == 404
    assert client.get("/api/customers").json()["total"] == 1


def test_viewer_cannot_write(client, db, user):
    user.role = "viewer"
    db.commit()
    assert client.post("/api/reconciliation").status_code == 403


def test_analyst_cannot_approve(client, db, user):
    user.role = "analyst"
    db.commit()
    assert (
        client.post(
            "/api/investigations/no-case/review",
            json={"decision": "approve", "note": "Review"},
            headers={"Idempotency-Key": "key123456"},
        ).status_code
        == 403
    )


def test_csrf_and_origin(client):
    assert (
        client.post("/api/reconciliation", headers={"Origin": "https://evil.example"}).status_code
        == 403
    )
    client.cookies.set("revenueops_session", "anything")
    assert client.post("/api/reconciliation").status_code == 403


def test_login_and_no_password_echo(client, db, user):
    user.password_hash = passwords.hash("Synthetic-test-123!")
    db.commit()
    result = client.post(
        "/api/auth/login", json={"email": user.email, "password": "Synthetic-test-123!"}
    )
    assert result.status_code == 200 and "httponly" in result.headers["set-cookie"].lower()
    assert "Synthetic-test-123!" not in result.text


def test_api_openapi_contract(client):
    schema = client.get("/openapi.json").json()
    assert "/api/investigations/{case_id}/review" in schema["paths"]
    assert schema["components"]["schemas"]["Decision"]["additionalProperties"] is False
