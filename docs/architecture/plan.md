# Implementation plan
Eight verified stages: foundation; financial persistence/import/matching; authorised
workflows/API; connected React console; CrewAI tools/crews/flow/durable worker;
evaluation/security; CI/CD/containers; final review/handover.

## Responsibility boundary
React → FastAPI → application services → PostgreSQL. Worker claims PostgreSQL jobs,
loads evidence, closes transactions, executes CrewAI, validates output and saves a
checkpoint. Reviewer API alone records allocations. Decimal balances are derived from
immutable allocations. Baseline mode never claims model execution.

## Environment inspection
Existing clean main branch, origin https://github.com/keenosmith-del/crewai-revenueops.git.
Initial commit 3d00352. Python 3.12 available alongside unsupported default Python 3.15;
Node 24.21, Docker 29.8.2 and Ollama llama3.2:3b available. No containers initially running.
AssessFlow AGENTS, iteration 008 and CI/release conventions reviewed read-only.
No push, cloud provisioning, messaging or paid model invocation authorised.

## Framework reference
Official CrewAI documentation consulted 2026-10-26: concepts/agents, tasks, crews,
flows, tools, llms and learn/human-feedback-in-flows at https://docs.crewai.com/.
Supported APIs selected: Agent, Task(output_pydantic, guardrail, guardrail_max_retries),
Crew(Process.sequential), BaseTool, Flow[typed state], start/listen/router and LLM.
Ollama requires crewai[litellm]. Application PostgreSQL checkpoints are authoritative;
no default SQLite Flow persistence. Human review is an authenticated durable HTTP
boundary, not terminal input or an AMP cloud dependency.
