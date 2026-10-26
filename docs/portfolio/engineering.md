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
accessible review forms, reports and local observability. Git preserves the eight original
implementation iterations plus Iteration 009 stages, each normally committed, pushed and
verified on actual hosted CI. Exact hashes/run URLs are in the iteration/release records.

Release evidence: CI definition includes PostgreSQL, financial/agent/flow/tool security,
frontend/build/browser, dependency and secret checks, Docker builds and API contracts.
All five hosted jobs passed for the CI correction and evaluation stages, including real
PostgreSQL integration, five browser workflows, 67 backend and 20 release tests, frontend
checks and linux/amd64 image builds. [Verified evaluation-stage run](https://github.com/keenosmith-del/crewai-revenueops/actions/runs/40354134960).
Prepared CD checks exact successful main CI, independent environment review, immutable
images, provenance labels, drift and recovery. No deployment was dispatched.

Lessons: a model advertising tools can still time out on a larger context. A small successful
probe does not prove agent accuracy. Framework transitive dependencies can carry unused
server advisories; remove optional dependency surfaces and document remaining exposure
rather than silently hiding scanner findings. Concurrency must be tested on PostgreSQL,
not inferred from SQLite success. Local source/build checks do not establish hosted release
or production correctness. See final handover for exact outcomes and limitations.

Iteration 009 expands model evidence beyond easy abstention probes. Four frozen ambiguous
cases share source evidence and independent ground truth: baseline 1/4 exact decisions,
actual local CrewAI 0/4. The model missed two supported matches, timed out once and failed
once, with 43 actual read-tool calls and no ledger writes. The benchmark exposes a model
limitation; it demonstrates neither accuracy improvement nor readiness to automate money.
The four existing unpatched Chroma server advisories remain explicitly scoped and expiring;
no dependency exception or guardrail was relaxed to obtain green CI.

The documentation stage independently passed all five hosted jobs at
4c78151ef9cb043026403d0371d1d7e163dcd062:
https://github.com/keenosmith-del/crewai-revenueops/actions/runs/40355395067.
The final receipt-only commit records this observed outcome; its own post-push verification
is reported in the final handover rather than predicted inside its own source tree.


## Iteration 010 — measured reliability limits

The evidence contract now supports a single scoped snapshot read, clear citation/raw IDs,
allowlisted lookup hints and source provenance. Ordinary ambiguity retains independent
investigator/quality tasks; active disputes retain the analyst. All exact citation,
financial, authorisation and human approval controls remain. Frontend design is unchanged.

The original four-case benchmark stays frozen: local llama3.2:3b remains **0/4** exact,
and completion regresses from 2/4 to 0/4. Tool success improves 30/43 to 8/8, with calls
43 to 8 and summed latency 489037ms to 195097ms, partly due to earlier validation failure.
Seven sealed holdouts achieve **1/7** exact vs baseline **4/7**, recovering one of three
supported allocation pairs, with five failed cases. Nine of eleven live cases fail typed
output; no accepted wrong pair or ledger write. Usage is retained, but historical failed
usage is unknown, so no token-efficiency improvement is claimed.

The same installed 3B model was used; no stronger local candidate was installed, no model
was downloaded, and no paid provider or infrastructure was used. Advertising tool calling
does not establish semantic or schema reliability. [Full results](../testing/iteration-010/results.md),
[methodology](../testing/iteration-010/methodology.md) and [stage record](../iterations/iteration-010.md)
retain all failures and qualify the tool improvement. No claim of improved investigation
accuracy, robust injection resistance, automatic finance readiness or production release.

PostgreSQL/backend/release: 100 passed; frontend: 5 passed; stage-2 hosted browser: 5 passed.
[Interface-stage CI](https://github.com/keenosmith-del/crewai-revenueops/actions/runs/40370217830)
succeeded in all five required jobs, including both container builds. Four reviewed Chroma
advisories remain unchanged. Deployment and provisioning remain unexecuted.
