import json
import logging
import time
from collections import defaultdict, deque
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.api.routes import auth, business
from app.core.config import settings
from app.db.session import SessionLocal

settings.validate_runtime()
app = FastAPI(title="RevenueOps Intelligence", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Requested-With"],
)
logger = logging.getLogger("revenueops.http")
attempts = defaultdict(deque)


@app.middleware("http")
async def controls(request: Request, call_next):
    correlation = str(uuid4())
    started = time.monotonic()
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        origin = request.headers.get("origin")
        if origin and origin not in settings.cors_origins:
            return JSONResponse({"detail": "Origin not permitted"}, status_code=403)
        if (
            request.cookies.get("revenueops_session")
            and request.headers.get("x-requested-with") != "RevenueOps"
        ):
            return JSONResponse({"detail": "CSRF header required"}, status_code=403)
    if request.url.path == "/api/auth/login":
        key = request.client.host
        queue = attempts[key]
        while queue and queue[0] < time.monotonic() - 60:
            queue.popleft()
        if len(queue) >= 20:
            return JSONResponse(
                {"detail": "Sign-in rate limited; retry in a minute"}, status_code=429
            )
        queue.append(time.monotonic())
    response = await call_next(request)
    response.headers.update(
        {
            "X-Correlation-ID": correlation,
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Cache-Control": "no-store",
            "Referrer-Policy": "no-referrer",
        }
    )
    logger.info(
        json.dumps(
            {
                "correlation_id": correlation,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": int((time.monotonic() - started) * 1000),
            }
        )
    )
    return response


@app.exception_handler(IntegrityError)
async def conflict(request, exc):
    return JSONResponse({"detail": "Conflicting record; refresh and retry"}, status_code=409)


@app.exception_handler(ValueError)
async def invalid(request, exc):
    return JSONResponse({"detail": str(exc)}, status_code=422)


@app.exception_handler(RequestValidationError)
async def validation(request, exc):
    # Never echo password, file contents or financial payloads in error responses.
    return JSONResponse(
        {
            "detail": [
                {"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()
            ]
        },
        status_code=422,
    )


@app.get("/health")
def health():
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"status": "ok", "service": "revenueops"}


app.include_router(auth.router, prefix="/api")
app.include_router(business.router, prefix="/api")
