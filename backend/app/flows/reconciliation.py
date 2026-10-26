from typing import Any, Literal

from crewai.flow.flow import Flow, listen, router, start
from pydantic import BaseModel, Field

from app.agents.crews.investigation import build_crew
from app.agents.tasks.validation import validate_findings


class ReconciliationState(BaseModel):
    id: str = ""
    investigation_id: str = ""
    transaction_id: str = ""
    stage: str = "investigation_required"
    classification: str = "unmatched"
    completed_steps: list[str] = Field(default_factory=list)
    result: dict = Field(default_factory=dict)
    usage: dict = Field(default_factory=dict)
    crew_id: str | None = None


class ReconciliationFlow(Flow[ReconciliationState]):
    context: dict = Field(default_factory=dict, exclude=True)
    llm: Any = Field(default=None, exclude=True)
    checkpoint: Any = Field(default=None, exclude=True)
    record_call: Any = Field(default=None, exclude=True)
    task_callback: Any = Field(default=None, exclude=True)
    validation_callback: Any = Field(default=None, exclude=True)

    def save(self, stage):
        self.state.stage = stage
        if stage not in self.state.completed_steps:
            self.state.completed_steps.append(stage)
        if self.checkpoint:
            self.checkpoint(self.state.model_dump())

    @start()
    def load_case(self):
        self.state.investigation_id = self.context["investigation_id"]
        self.state.transaction_id = self.context["transaction_id"]
        self.state.classification = self.context["classification"]
        self.save("exception_classification")

    @router(load_case)
    def route(self) -> Literal["resume", "deterministic", "investigate", "dispute", "collections"]:
        if self.state.result:
            return "resume"
        if self.context.get("purpose") == "collections":
            return "collections"
        if self.state.classification == "exact":
            return "deterministic"
        if self.state.classification in ("disputed", "duplicate", "reversal") or any(
            key.startswith("dispute:") and record.get("status") == "open"
            for key, record in self.context["records"].items()
        ):
            return "dispute"
        return "investigate"

    def execute(self, dispute=False, collections=False):
        self.save("dispute_analysis" if dispute else "reconciliation_investigation")
        crew = build_crew(
            self.context,
            self.llm,
            dispute=dispute,
            collections=collections,
            record_call=self.record_call,
            task_callback=self.task_callback,
            validation_callback=self.validation_callback,
        )
        self.state.crew_id = str(crew.id)
        self.save("crew_started")
        try:
            output = crew.kickoff()
        finally:
            metrics = crew.calculate_usage_metrics()
            self.state.usage = metrics.model_dump() if metrics else {}
        result = validate_findings(output.pydantic, self.context)
        self.state.result = result.model_dump()
        self.save("quality_review")
        self.save("human_review")
        return self.state.result

    @listen("investigate")
    def run_investigation(self):
        return self.execute()

    @listen("dispute")
    def run_dispute(self):
        return self.execute(dispute=True)

    @listen("deterministic")
    def deterministic_review(self):
        self.save("human_review")
        return {"mode": "deterministic_only", "required_human_action": "Review exact proposal"}

    @listen("resume")
    def resume_result(self):
        self.save("human_review")
        return self.state.result

    @listen("collections")
    def run_collections(self):
        return self.execute(collections=True)
