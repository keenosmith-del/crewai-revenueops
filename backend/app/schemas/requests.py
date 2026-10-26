from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Login(Strict):
    email: str = Field(max_length=180)
    password: str = Field(max_length=200)


class AllocationInput(Strict):
    invoice_id: str = Field(max_length=36)
    amount: str = Field(max_length=30)


class Decision(Strict):
    decision: Literal["approve", "reject", "request_information"]
    note: str = Field(min_length=3, max_length=1000)
    allocations: list[AllocationInput] | None = Field(default=None, max_length=30)


class DisputeInput(Strict):
    note: str = Field(min_length=5, max_length=2000)


class DraftInput(Strict):
    invoice_id: str = Field(max_length=36)


class DraftDecision(Strict):
    decision: Literal["approve", "reject"]


class CustomerInput(Strict):
    name: str = Field(min_length=2, max_length=160)
    account: str = Field(min_length=2, max_length=60, pattern=r"^[A-Za-z0-9_-]+$")
    email: str = Field(max_length=180, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class VerifyAccount(Strict):
    customer_id: str = Field(max_length=36)
    note: str = Field(min_length=5, max_length=1000)
