from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Evidence(Strict):
    reference: str = Field(max_length=100)
    field: str = Field(max_length=60)
    value: str = Field(max_length=1000)


class ProposedAllocation(Strict):
    invoice_id: str = Field(max_length=36)
    amount: str = Field(pattern=r"^\d+(\.\d{1,3})?$", max_length=30)


class Findings(Strict):
    investigation_id: str
    transaction_id: str
    currency: str = Field(min_length=3, max_length=3)
    allocations: list[ProposedAllocation] = Field(default_factory=list, max_length=30)
    summary: str = Field(min_length=10, max_length=1500)
    evidence: list[Evidence] = Field(min_length=1, max_length=30)
    uncertainty: Literal["low", "medium", "high"]
    recommendation: Literal[
        "propose_allocation", "request_information", "escalate", "draft_followup"
    ]
    missing_information: list[str] = Field(default_factory=list, max_length=10)
    validation_findings: list[str] = Field(default_factory=list, max_length=10)
    required_human_action: str = Field(min_length=5, max_length=500)
    draft_message: str | None = Field(default=None, max_length=2000)
