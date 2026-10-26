# RevenueOps Intelligence — engineering handover

## Delivered system
A connected financial operations application with PostgreSQL persistence, authenticated
FastAPI services, React operational console, deterministic reconciliation, conservative
human approvals, actual CrewAI investigation and durable worker execution. The normal
local demo runs at http://localhost:5174 (API localhost:5051); PostgreSQL uses 55433.
These containers are local development services with labelled synthetic records.

## Responsibility and architecture
The database and Decimal application services own financial truth. Allocations derive
balances, require current organisation-scoped records and reviewer permissions, lock
records in a consistent order, and atomically write financial history, decisions, audit
and idempotency results. No agent tool can mutate the ledger or send a communication.
The API handles imports, batches, disputes, account verification, review, drafts and reports.
React supplies a shared cream/charcoal interface with separate JSX/CSS page folders.
Architecture, sequence and ERD diagrams are in docs/architecture/system.md.

## Crew and Flow implementation
CrewAI 1.15.30 is an active architectural component. Four YAML-configured roles:
reconciliation investigator, billing/dispute analyst, collections coordinator, quality
reviewer. Sequential crews share preceding Task outputs through explicit context.
Exact matches bypass inference; conflicts add the analyst; collections has its own branch.
One narrowly scoped BaseTool exposes only allowed invoice/transaction/customer/dispute
fields from an organisation-bounded snapshot. No SQL, shell, filesystem, mutation or
sending interface is available. Task output_pydantic and guardrails validate case identity,
field/value citations and candidate invoice IDs; fresh application financial validation
is authoritative. Findings store concise explanations and evidence, not hidden reasoning.

Typed Flow start/router/listen methods checkpoint application state to PostgreSQL.
Workers claim leased rows with SKIP LOCKED, fence stale owners, release DB transactions
before inference, bound child runtime and record task/tool outcomes. A persisted result
resumes without another provider request (tested) and cannot replay ledger actions.
Failed inference is stored explicitly. The model/provider/usage/timing fields distinguish
baseline, deterministic-only and actual local runs. No fabricated agent animation exists.

## Product and database
Operational pages: overview with date/currency filters, invoices/details/disputes,
transactions/import history/account verification, reconciliation/batches, investigations
with invoice/amount review controls, customer history/timeline, Agent workspace, collections,
reports/export/evaluation evidence, audit, settings and sign-in. Loading/empty/error/search,
status filters, sorting, pagination, responsive navigation and reduced motion are included.

Normalised records cover organisations/users, customers, imports, invoices, transactions,
batches, investigations, allocations, reviews, disputes, drafts, executions/tool calls,
audit and idempotency. Typed evidence and Flow state use versioned JSON structures.
No redundant mutable balance is trusted. PostgreSQL is primary; SQLite is confined to
isolated fast tests and the known-truth benchmark.

## Verification, evaluation and Git evidence
Iteration 009 verification: **87 PostgreSQL/release tests passed locally** (67 backend,
20 release), plus **5 frontend tests and 5 isolated browser workflows passed on GitHub**.
All five hosted jobs passed on the CI correction and evaluation stages; exact receipts
and hashes are in docs/iterations/iteration-009.md and release-manifest.json. Historical
Iteration 008 coverage was 81%; no new coverage percentage was measured for this iteration.
Migrations, financial invariants, organisation isolation, idempotency, read-only tools,
worker recovery, API contracts, dependency checks, secrets and container builds are verified.

The 13-case deterministic regression set remains 13/13. The new four-case investigation
benchmark uses identical evidence and independent ground truth: **baseline 1/4, assisted
0/4**. Both supported matches were missed by model abstention; the two other cases timed
out or failed. 43 actual read-tool calls, 489037ms total measured case latency, zero ledger
writes. The earlier successful small crew and three easy abstention cases remain historical
evidence, not proof of useful ambiguous-match recovery. No model improvement is claimed.
Model digest, concise outputs, failures and limitations are preserved without hidden reasoning.

Normal pushes and actual GitHub branch/run inspection verify the stage commits on main.
No force-push, history rewriting, failing-check bypass or unrelated changes occurred.

## Security and operations
Live-role RBAC, organisation scoping, signed expiring HttpOnly/SameSite cookies, Argon2,
origin/CSRF controls, production configuration gates, import limits, formula-safe export,
immutable API history and audited customer verification are implemented. No demo identity
headers, sender or payment executor exist. Token usage is reported only as supplied by
CrewAI; estimated money cost is unmeasured. Model telemetry exports are disabled.

Python retains four unpatched advisories in unused transitive Chroma server paths;
reviewed, exact-version exceptions expire 2026-11-26. No Chroma server, knowledge or memory
is enabled. Frontend audit is clean. No claim of zero residual security risk is made.
Use private DB networking, HTTPS, random production secrets, shared edge rate limits,
managed backups and restricted operator accounts before exposing real data.

## CI/CD and deployment readiness
verify.yml covers PostgreSQL migrations/financial/agent/flow/security tests, release tests,
API contracts, frontend checks/build/browser, dependency/secret checks and images. Ordinary
CI requires no paid inference. Gated deploy-staging.yml targets existing Linux staging,
requires independent environment review and exact successful main CI source, publishes
and promotes digest references, verifies revision labels, rejects baseline drift and saves
recovery evidence. Rollback uses a reviewed prior image pair, not a rebuild or DB downgrade.

Hosted Verify RevenueOps is now **verified successful**, including the fixed PostgreSQL
services and linux/amd64 container builds. The latest documented code/evaluation receipt:
https://github.com/keenosmith-del/crewai-revenueops/actions/runs/40354134960 at
8d48c26ac1e351a4357a012f3893a7e2e06a208e. Documentation commit 4c78151ef9cb043026403d0371d1d7e163dcd062 also passed all five jobs:
https://github.com/keenosmith-del/crewai-revenueops/actions/runs/40355395067. Exact stage
receipts are recorded after observing their successful pushes and hosted runs.

CD remains prepared only. Inspection found no configured GitHub environment and zero
deployment-workflow runs. No registry publish, staging host, credentials, infrastructure
or production operation was activated. Successful CI is not production certification.

## Startup and model configuration
Exact native/container commands, sign-in and isolated browser setup: docs/deployment/local.md.
Quick existing-checkout startup:
```sh
docker compose up -d --build
docker compose exec api python -m app.db.seed
```
Local configured ports: web 5174, API 5051. A new checkout defaults to 5173/5050.
Synthetic reviewer@revenueops.example / Demo-finance-2026!. Native provider: MODEL_MODE=ollama,
OLLAMA_MODEL=llama3.2:3b, OLLAMA_URL=http://localhost:11434. Docker Desktop URL:
http://host.docker.internal:11434. Restart API/worker after environment changes. Native
OpenAI-compatible transport is local and does not require paid OpenAI credentials.
Hosted native OpenAI mode requires explicit HOSTED_ENABLED, model and credentials; it
was not enabled. Baseline mode remains fully functional and clearly records not_executed.

## Remaining engineering limits
No PDF/OCR, bank integration, FX, live payments, accounting adjustments/general ledger,
external mail, SSO/MFA/password recovery, high availability or scale certification.
List pagination currently filters in memory; optimise SQL queries before large datasets.
AI collection drafts require one eligible invoice in scope; ordinary reviewed templates
work per invoice. Larger-case model reliability and comprehensive semantic assertions
need further evaluation. Worker process supervision/provider edge cases are not fully
covered despite persisted resume/fencing tests and real local probes. Hosted CI and
linux/amd64 image builds passed; registry publishing and staging/rollback remain unexecuted
and require separate authorisation/configuration. The current local model is unreliable
on the new ambiguous set; financial human review and strict validators remain mandatory.
