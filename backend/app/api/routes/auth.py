from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select

from app.core.config import settings
from app.db.session import get_db
from app.models.entities import Organisation, User
from app.schemas.requests import Login
from app.security.auth import current_user, passwords, token
from app.services.ledger import audit

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login(body: Login, response: Response, db=Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email, User.active.is_(True)))
    # Verify a fixed valid hash even for an unknown identity to avoid a trivial timing oracle.
    valid = passwords.verify(body.password, user.password_hash if user else DUMMY_HASH)
    if not user or not valid:
        raise HTTPException(401, "Invalid credentials")
    response.set_cookie(
        "revenueops_session",
        token(user),
        httponly=True,
        secure=settings.app_env == "production",
        samesite="strict",
        max_age=14400,
        path="/",
    )
    audit(db, user, "auth.login", user.id)
    db.commit()
    return {"id": user.id, "email": user.email, "role": user.role}


DUMMY_HASH = passwords.hash("not-a-user-password")


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("revenueops_session", path="/")
    return {"status": "signed_out"}


@router.get("/me")
def me(user=Depends(current_user), db=Depends(get_db)):
    org = db.get(Organisation, user.org_id)
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "organisation": org.name,
        "synthetic": org.synthetic,
    }
