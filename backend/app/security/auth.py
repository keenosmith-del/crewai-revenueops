from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy import select

from app.core.config import settings
from app.db.session import get_db
from app.models.entities import User

passwords = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)


def token(user):
    return jwt.encode(
        {
            "sub": user.id,
            "org": user.org_id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=4),
            "iss": "revenueops",
            "aud": "revenueops-api",
        },
        settings.jwt_secret,
        algorithm="HS256",
    )


def current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db=Depends(get_db),
):
    raw = credentials.credentials if credentials else request.cookies.get("revenueops_session")
    if not raw:
        raise HTTPException(401, "Sign in required")
    try:
        payload = jwt.decode(
            raw,
            settings.jwt_secret,
            algorithms=["HS256"],
            issuer="revenueops",
            audience="revenueops-api",
        )
        user = db.scalar(
            select(User).where(
                User.id == payload["sub"], User.org_id == payload["org"], User.active.is_(True)
            )
        )
        if not user:
            raise ValueError("Inactive identity")
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise HTTPException(401, "Session invalid or expired") from exc
    return user


def require(*roles):
    def dependency(user=Depends(current_user)):
        if user.role not in roles:
            raise HTTPException(403, "Role does not permit this action")
        return user

    return dependency


operator = require("admin", "analyst", "reviewer")
reviewer = require("admin", "reviewer")
admin = require("admin")
