from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def uid():
    return str(uuid4())


def now():
    return datetime.now(timezone.utc)


class Identity:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)


class Scoped(Identity):
    org_id: Mapped[str] = mapped_column(ForeignKey("organisations.id"), index=True)


class Organisation(Identity, Base):
    __tablename__ = "organisations"
    name: Mapped[str] = mapped_column(String(160))
    synthetic: Mapped[bool] = mapped_column(Boolean, default=False)


class User(Scoped, Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(180), unique=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    role: Mapped[str] = mapped_column(String(30))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Customer(Scoped, Base):
    __tablename__ = "customers"
    __table_args__ = (UniqueConstraint("org_id", "account"),)
    name: Mapped[str] = mapped_column(String(160))
    account: Mapped[str] = mapped_column(String(60))
    email: Mapped[str] = mapped_column(String(180))


class Import(Scoped, Base):
    __tablename__ = "imports"
    __table_args__ = (UniqueConstraint("org_id", "kind", "source_hash"),)
    kind: Mapped[str] = mapped_column(String(30))
    source_hash: Mapped[str] = mapped_column(String(64))
    filename: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(30), default="preview")
    rows: Mapped[list] = mapped_column(JSON)
    errors: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Invoice(Scoped, Base):
    __tablename__ = "invoices"
    __table_args__ = (UniqueConstraint("org_id", "reference"), CheckConstraint("amount > 0"))
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), index=True)
    reference: Mapped[str] = mapped_column(String(100))
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 3))
    currency: Mapped[str] = mapped_column(String(3))
    issue_date: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date] = mapped_column(Date)
    import_id: Mapped[str | None] = mapped_column(ForeignKey("imports.id"))


class Transaction(Scoped, Base):
    __tablename__ = "transactions"
    __table_args__ = (UniqueConstraint("org_id", "source_id"), CheckConstraint("amount != 0"))
    customer_id: Mapped[str | None] = mapped_column(ForeignKey("customers.id"), index=True)
    source_id: Mapped[str] = mapped_column(String(100))
    reference: Mapped[str] = mapped_column(String(200))
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 3))
    currency: Mapped[str] = mapped_column(String(3))
    payment_date: Mapped[date] = mapped_column(Date)
    duplicate_of: Mapped[str | None] = mapped_column(ForeignKey("transactions.id"))
    import_id: Mapped[str | None] = mapped_column(ForeignKey("imports.id"))


class Batch(Scoped, Base):
    __tablename__ = "batches"
    status: Mapped[str] = mapped_column(String(30), default="completed")
    summary: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Investigation(Scoped, Base):
    __tablename__ = "investigations"
    __table_args__ = (UniqueConstraint("org_id", "transaction_id"),)
    transaction_id: Mapped[str] = mapped_column(ForeignKey("transactions.id"))
    batch_id: Mapped[str] = mapped_column(ForeignKey("batches.id"))
    classification: Mapped[str] = mapped_column(String(60))
    status: Mapped[str] = mapped_column(String(40), default="human_review")
    proposal: Mapped[dict] = mapped_column(JSON, default=dict)
    explanation: Mapped[str] = mapped_column(String(1000), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Allocation(Scoped, Base):
    __tablename__ = "allocations"
    __table_args__ = (
        UniqueConstraint("org_id", "investigation_id", "invoice_id"),
        CheckConstraint("amount > 0"),
    )
    transaction_id: Mapped[str] = mapped_column(ForeignKey("transactions.id"), index=True)
    invoice_id: Mapped[str] = mapped_column(ForeignKey("invoices.id"), index=True)
    investigation_id: Mapped[str] = mapped_column(ForeignKey("investigations.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 3))
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Review(Scoped, Base):
    __tablename__ = "reviews"
    investigation_id: Mapped[str] = mapped_column(ForeignKey("investigations.id"))
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    decision: Mapped[str] = mapped_column(String(30))
    note: Mapped[str] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Dispute(Scoped, Base):
    __tablename__ = "disputes"
    invoice_id: Mapped[str] = mapped_column(ForeignKey("invoices.id"), index=True)
    note: Mapped[str] = mapped_column(String(2000))
    status: Mapped[str] = mapped_column(String(30), default="open")
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Draft(Scoped, Base):
    __tablename__ = "drafts"
    invoice_id: Mapped[str] = mapped_column(ForeignKey("invoices.id"))
    body: Mapped[str] = mapped_column(String(4000))
    status: Mapped[str] = mapped_column(String(30), default="draft")
    source: Mapped[str] = mapped_column(String(30), default="deterministic_template")
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Execution(Scoped, Base):
    __tablename__ = "executions"
    investigation_id: Mapped[str] = mapped_column(ForeignKey("investigations.id"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="queued", index=True)
    mode: Mapped[str] = mapped_column(String(30))
    model: Mapped[str] = mapped_column(String(120), default="")
    stage: Mapped[str] = mapped_column(String(60), default="queued")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    lease_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    lease_token: Mapped[str | None] = mapped_column(String(36))
    checkpoint: Mapped[dict] = mapped_column(JSON, default=dict)
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[str | None] = mapped_column(String(500))
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    usage: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class ToolCall(Scoped, Base):
    __tablename__ = "tool_calls"
    execution_id: Mapped[str] = mapped_column(ForeignKey("executions.id"))
    name: Mapped[str] = mapped_column(String(80))
    record_id: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30))
    duration_ms: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Audit(Scoped, Base):
    __tablename__ = "audit_events"
    actor_id: Mapped[str] = mapped_column(String(80))
    action: Mapped[str] = mapped_column(String(80), index=True)
    record_id: Mapped[str] = mapped_column(String(100), index=True)
    correlation_id: Mapped[str] = mapped_column(String(36), default=uid)
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Idempotency(Scoped, Base):
    __tablename__ = "idempotency"
    __table_args__ = (UniqueConstraint("org_id", "key"),)
    key: Mapped[str] = mapped_column(String(100))
    fingerprint: Mapped[str] = mapped_column(String(64))
    result: Mapped[dict] = mapped_column(JSON)
