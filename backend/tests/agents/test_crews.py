import json

import pytest
from crewai import BaseLLM
from pydantic import Field

from app.agents.crews.investigation import build_crew
from app.agents.tasks.validation import validate_findings
from app.agents.tools.evidence import FinancialEvidenceTool
from app.core.config import settings  # noqa: F401
from app.flows.reconciliation import ReconciliationFlow

CONTEXT = {
    "investigation_id": "case",
    "transaction_id": "tx",
    "classification": "unmatched",
    "currency": "ZAR",
    "records": {"transaction:tx": {"reference": "invoice missing", "amount": "100.000"}},
}
FINDING = {
    "investigation_id": "case",
    "transaction_id": "tx",
    "currency": "ZAR",
    "allocations": [],
    "summary": "Payment reference requires customer clarification.",
    "evidence": [{"reference": "transaction:tx", "field": "amount", "value": "100.000"}],
    "uncertainty": "high",
    "recommendation": "request_information",
    "missing_information": ["Invoice reference"],
    "validation_findings": [],
    "required_human_action": "Verify the invoice with the customer",
    "draft_message": None,
}


class ContractLLM(BaseLLM):
    model: str = "mocked-contract-test"
    responses: list[str] = Field(default_factory=list)
    calls: int = 0

    def call(self, messages, **kwargs):
        self.calls += 1
        return self.responses.pop(0) if self.responses else "Final Answer: " + json.dumps(FINDING)

    def supports_function_calling(self):
        return False


def test_real_crew_collaboration_mocked_inference():
    llm = ContractLLM(model="mocked-contract-test")
    completed = []
    crew = build_crew(
        CONTEXT, llm, dispute=True, task_callback=lambda output: completed.append(output.agent)
    )
    assert len(crew.agents) == 3 and len(crew.tasks) == 3
    assert len(crew.tasks[-1].context) == 2
    result = crew.kickoff()
    assert result.pydantic.transaction_id == "tx"
    assert len(completed) == 3 and llm.calls >= 3
    assert all(not agent.allow_delegation for agent in crew.agents)


def test_tool_is_allowlisted_read_only():
    calls = []
    tool = FinancialEvidenceTool(
        records=CONTEXT["records"], record_call=lambda *args: calls.append(args)
    )
    assert json.loads(tool._run("transaction", "tx"))["record"]["amount"] == "100.000"
    assert json.loads(tool._run("invoice", "other-org"))["status"] == "not_found"
    assert calls[-1][2] == "not_found"
    assert not hasattr(tool, "execute_sql")


@pytest.mark.parametrize(
    "kind", ["invented", "wrong_value", "identity", "currency", "contradiction"]
)
def test_guardrails(kind):
    result = json.loads(json.dumps(FINDING))
    if kind == "invented":
        result["evidence"][0]["reference"] = "invoice:invented"
    if kind == "wrong_value":
        result["evidence"][0]["value"] = "999"
    if kind == "identity":
        result["transaction_id"] = "other"
    if kind == "currency":
        result["currency"] = "USD"
    if kind == "contradiction":
        result["recommendation"] = "propose_allocation"
    with pytest.raises(ValueError):
        validate_findings(result, CONTEXT)


def test_flow_conditional_and_resume():
    checkpoints = []
    context = {**CONTEXT, "classification": "exact"}
    flow = ReconciliationFlow(context=context, checkpoint=checkpoints.append)
    result = flow.kickoff()
    assert result["mode"] == "deterministic_only"
    assert checkpoints[-1]["stage"] == "human_review"
    resumed = ReconciliationFlow(context=CONTEXT, llm=None)
    resumed.kickoff(inputs={"result": FINDING})
    assert resumed.state.result == FINDING


def test_flow_executes_actual_crew_with_mocked_inference():
    flow = ReconciliationFlow(context=CONTEXT, llm=ContractLLM(model="mocked-contract-test"))
    flow.kickoff()
    assert flow.state.stage == "human_review"
    assert flow.state.result["recommendation"] == "request_information"


def test_collections_composition():
    crew = build_crew(CONTEXT, ContractLLM(model="mocked-contract-test"), collections=True)
    assert len(crew.agents) == 2
    assert crew.tasks[0].name == "collections"


class UnavailableLLM(ContractLLM):
    def call(self, messages, **kwargs):
        raise ConnectionError("Synthetic model unavailable")


def test_model_failure_never_produces_recommendation():
    flow = ReconciliationFlow(context=CONTEXT, llm=UnavailableLLM(model="mocked-unavailable"))
    with pytest.raises(Exception):
        flow.kickoff()
    assert flow.state.result == {}


def test_actual_guardrail_rejects_fabricated_citation():
    from crewai.tasks.task_output import TaskOutput

    from app.agents.tasks.validation import guardrail

    fabricated = {
        **FINDING,
        "evidence": [{"reference": "invoice:fake", "field": "amount", "value": "100"}],
    }
    outcome = guardrail(CONTEXT)(
        TaskOutput(description="Synthetic invalid output", raw=json.dumps(fabricated), agent="mock")
    )
    assert outcome[0] is False


def test_snapshot_and_prefixed_ids_cannot_expand_allowlist():
    tool = FinancialEvidenceTool(records=CONTEXT["records"])
    assert json.loads(tool._run("snapshot", "all"))["record"] == CONTEXT["records"]
    assert json.loads(tool._run("transaction", "transaction:tx"))["status"] == "ok"
    missing = json.loads(tool._run("invoice", "transaction:tx"))
    assert missing["status"] == "not_found"
    assert missing["allowed_references"] == ["transaction:tx"]
    assert (
        json.loads(tool._run("transaction", "transaction:transaction:tx"))["status"] == "not_found"
    )


def test_ambiguity_keeps_two_independent_reviewers_and_open_disputes_add_specialist():
    context = {**CONTEXT, "classification": "ambiguous"}
    flow = ReconciliationFlow(context=context)
    flow.load_case()
    assert flow.route() == "investigate"
    flow.context["records"] = {**CONTEXT["records"], "dispute:d": {"status": "open"}}
    assert flow.route() == "dispute"


def test_validation_failures_are_observed_without_accepting_invalid_output():
    from crewai.tasks.task_output import TaskOutput

    from app.agents.tasks.validation import guardrail

    events = []
    valid = guardrail(CONTEXT, lambda *event: events.append(event))
    assert valid(TaskOutput(description="Synthetic", raw="{}", agent="mock"))[0] is False
    assert events == [("rejected", "ValidationError")]
