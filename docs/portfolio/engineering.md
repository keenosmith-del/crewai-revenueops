# Engineering portfolio
RevenueOps demonstrates separation of financial truth, agent interpretation and human
responsibility. The core uses exact Decimal values, transactional imports, conservative
matching, idempotent approvals and tested PostgreSQL concurrency. Agents collaborate
through task context and scoped evidence, with deterministic validation after model output.
The React console exercises real persistent workflows; it is not an animated agent mockup.

CrewAI evidence: pinned framework; YAML roles/tasks; four distinct specialists; actual
BaseTool implementation; typed Flow with conditional branches; structured Pydantic output;
callable guardrails; short-session PostgreSQL checkpoints; explicit human boundary;
fenced durable worker; real local model success and failure records. Mocked inference is
clearly isolated in contract tests. No model is entrusted with ledger authority.

Full-stack evidence: normalised PostgreSQL/Alembic, FastAPI/OpenAPI, authentication/RBAC,
organisation isolation, safe CSV preview/commit/export, React Router pages, shared CSS,
accessible review forms, reports and local observability. Git records eight meaningful
implementation stages plus any factual manifest update needed to record final hashes.

Release evidence: CI definition includes PostgreSQL, financial/agent/flow/tool security,
frontend/build/browser, dependency and secret checks, Docker builds and API contracts.
Prepared CD checks exact successful main CI, independent environment review, immutable
images, provenance labels, drift and recovery. No hosted run or deployment is fabricated.

Lessons: a model advertising tools can still time out on a larger context. A small successful
probe does not prove agent accuracy. Framework transitive dependencies can carry unused
server advisories; remove optional dependency surfaces and document remaining exposure
rather than silently hiding scanner findings. Concurrency must be tested on PostgreSQL,
not inferred from SQLite success. Local source/build checks do not establish hosted release
or production correctness. See final handover for exact outcomes and limitations.
