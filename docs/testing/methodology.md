# Test and evaluation methodology
Unit checks use an isolated SQLite database for fast feedback. Production and integration
checks use PostgreSQL 17; the concurrency test skips on SQLite because it cannot prove
row-lock semantics. TEST_DATABASE_URL must name a disposable database ending _test.
The fixture drops only that explicitly configured test schema; never point it at business data.

Known-truth benchmark data/evaluations/cases.json has 13 independently specified cases:
exact, partial, overpayment, combined, missing/wrong reference, unmatched, reversal,
duplicate, disputed, cross-currency, ambiguous and injected reference. Evaluation checks
classification and exact proposed Decimal allocations, then computes proposal precision
and recall. This is a small constructed regression benchmark, not a production accuracy estimate.

CrewAI tests execute real agents, tasks, sequential crews and Flow routing with a labelled
ContractLLM. Those check framework integration, context collaboration, schema/guardrails,
restricted tool behaviour and state resumption. They do not establish live reasoning quality.

Live evidence is separate: docs/testing/live-model.json records the first larger-case
Ollama timeout (one tool call, no completed task), and live-small-model.json records the
successful two-agent local-native-provider execution, tool count and reported token usage.
Neither single-case probe is a statistically meaningful baseline improvement measurement.
No hosted inference or cost estimate is fabricated. The benchmark reports this limitation.

Browser checks exercise the actual API and PostgreSQL: login, reconcile, approve and
reload persisted allocation, inspect audit, preview/confirm CSV and approve-not-send draft,
mobile navigation and overflow checks. The first desktop screenshot initially caught a
loading state; the final test waits for financial data before capturing evidence.

Commands from repository root:
```sh
.venv/bin/ruff check backend scripts
.venv/bin/ruff format --check backend scripts
.venv/bin/pytest -q backend/tests
TEST_DATABASE_URL=postgresql+psycopg://revenueops:local-only@localhost:55433/revenueops_test .venv/bin/pytest -q backend/tests
PYTHONPATH=backend .venv/bin/python -m app.evaluations.runner
.venv/bin/python scripts/check_contracts.py
.venv/bin/python scripts/check_dependencies.py
npm --prefix frontend run lint
npm --prefix frontend test
npm --prefix frontend run build
npm --prefix frontend run test:e2e
```
Start the services first for browser checks. Playwright default URL is localhost:5174;
E2E_URL overrides it. Seeded database required. No test starts a paid model or sends mail.
