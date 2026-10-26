# RevenueOps Intelligence

[![Verify RevenueOps](https://github.com/keenosmith-del/crewai-revenueops/actions/workflows/verify.yml/badge.svg)](https://github.com/keenosmith-del/crewai-revenueops/actions/workflows/verify.yml)

A financial operations workspace for accounts receivable, payment reconciliation,
evidence-backed investigation and responsible collections. **Deterministic software owns
the ledger, CrewAI investigates, and finance reviewers authorise allocations.**

Built with Python 3.12, FastAPI, Pydantic, SQLAlchemy/Alembic, PostgreSQL 17, CrewAI 1.15.30,
React JSX, Vite, React Router, plain CSS and native Fetch. No paid service is required for
the baseline application. All included business records and identities are synthetic.

## What works

- Invoice and bank CSV templates, column mapping, validation preview, row errors,
  atomic confirmation, source provenance and duplicate protection.
- Decimal matching for exact references, customer/amount, partial receipts, overpayments,
  combined invoices, ambiguities, disputes, reversals and suspected duplicates.
- Authenticated reviewer decisions with fresh financial validation, transaction locks,
  idempotency, immutable allocations and auditable balance changes.
- Connected dashboard, invoices/details, transactions, reconciliation, investigations,
  customer history, Agent workspace, collections, reports, audit, settings and sign-in.
- Four specialist CrewAI roles, conditional crews, task-context collaboration, scoped
  read-only BaseTool, structured outputs, citation guardrails and typed Flow routing.
- PostgreSQL job leases, fencing, bounded inference, persisted checkpoints and resume
  without repeated completed inference or ledger posting.
- Respectful overdue follow-up drafts and internal approval; **no message sender exists**.
- Local execution/tool/task observability and reproducible baseline/live evaluation evidence.

## Verification and release status

See [actual results](docs/testing/results.md), [handover](docs/portfolio/handover.md) and
[release manifest](docs/iterations/release-manifest.json) for exact evidence and Git hashes.
Local PostgreSQL, framework contracts, browser workflows, builds and a small genuine
Ollama crew have been exercised. Live comparison: deterministic baseline and CrewAI both
handled 3/3 selected exceptions safely. Larger model cases timed out or failed validation;
no general accuracy improvement is claimed. Mocked inference is labelled separately.

GitHub Actions CI and a separately gated existing-staging deployment workflow are prepared.
**No push, hosted CI run, environment activation or deployment has occurred.** The badge
links to the real workflow path and does not imply a successful hosted run.

Python security review retains four unpatched ChromaDB server advisories in a transitive
CrewAI dependency. No Chroma server, memory or knowledge feature is enabled. Exact scoped,
expiring exceptions are [documented](docs/security/dependency-exceptions.json); new or
expired findings fail the check. This is not a zero-vulnerability claim. Frontend audit is clean.

## Run locally

Full [native/container setup and model configuration](docs/deployment/local.md).
From the repository root, with Python 3.12, Node 24 and Docker available:

```sh
python3.12 -m venv .venv
.venv/bin/pip install -r backend/requirements-lock.txt
cp .env.example .env
# Set a random JWT_SECRET; keep development, demo and baseline mode for synthetic use.
docker compose up -d --build
# Wait for API health, then seed the synthetic workspace:
docker compose exec api python -m app.db.seed
```

Open [the local console](http://localhost:5173). Sign in as
`reviewer@revenueops.example` / `Demo-finance-2026!`. Synthetic admin, analyst and viewer
identities use the corresponding email prefix and the same demo-only password. Ports
5050/5173 are defaults; `API_PORT` and `WEB_PORT` override them. The implementation session
used 5051/5174 to preserve existing services. The PostgreSQL port is 55433.

To use local Ollama, configure `MODEL_MODE=ollama`, `OLLAMA_MODEL=llama3.2:3b` and the
appropriate local URL, then restart API/worker. Native processes use localhost:11434;
Docker Desktop uses host.docker.internal:11434. Baseline mode explicitly records agent
requests as **not executed**. Hosted inference requires separate explicit activation and credentials.

For real identities, disable demo mode, configure production secrets/HTTPS/private data
access, and provision accounts using the password-prompt operator CLI:
`python -m app.security.provision --organisation NAME --email ADDRESS --role reviewer`.
Production rejects demo mode and placeholder secrets. Review the security limitations
before introducing real financial data.

## Verify

```sh
.venv/bin/ruff check backend scripts tests
.venv/bin/ruff format --check backend scripts tests
.venv/bin/pytest -q backend/tests tests/release
TEST_DATABASE_URL=postgresql+psycopg://revenueops:local-only@localhost:55433/revenueops_test .venv/bin/pytest -q backend/tests tests/release
PYTHONPATH=backend .venv/bin/python -m app.evaluations.runner
.venv/bin/python scripts/check_contracts.py
.venv/bin/python scripts/check_dependencies.py
npm --prefix frontend run lint
npm --prefix frontend test
npm --prefix frontend run build
```

PostgreSQL test databases must be disposable and end in `_test`; the fixture recreates
only that schema. Browser write tests require the [isolated test service](docs/deployment/local.md#isolated-browser-verification),
not the main demo ledger. Ordinary CI uses mocked model responses for contracts while
actually exercising CrewAI; no paid inference is required.

## Repository and engineering notes

`backend/app` separates API, services, repositories, accounting, reconciliation, agents,
Flows, providers, security and workers. `frontend/src/pages` has matching JSX/CSS per page.
`data` contains templates, synthetic records and labelled evaluation cases. `docs` covers
product requirements, architecture/ERD/sequences, decisions, agents, financial controls,
API, security, testing, deployment, operations, portfolio and verified Git iterations.

Start with [architecture](docs/architecture/system.md), [CrewAI engineering](docs/agents/engineering.md),
[financial controls](docs/financial/controls.md), [API](docs/api/contracts.md),
[security](docs/security/threat-model.md), [operations](docs/operations/runbook.md) and
[staging preparation](docs/deployment/staging.md).

Current limits: CSV only; no PDF/OCR, banking integration, live payments, FX conversion,
credit notes, general-ledger posting, email transport, SSO/MFA/password recovery, high
availability or large-scale performance certification. List pagination currently filters
in memory for this demonstration dataset. AI collection drafts require one eligible
invoice in scope; multi-invoice follow-ups use explicit reviewed template drafts. Live
model reliability needs broader evaluation. Production deployment remains unverified.
