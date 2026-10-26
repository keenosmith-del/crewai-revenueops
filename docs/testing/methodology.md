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
The later live-main-model.json records a larger native-adapter case rejected with ValidationError after 23 tool calls; no balances changed.
The three-case live-comparison.json compares actual deterministic outcomes with actual
local crews for unmatched, cross-currency and injected-reference cases. Both scored 3/3
on safe exception handling, with 3 tool calls per case. This small selected sample does
not establish a statistically meaningful baseline improvement. Framework token counts may
include approximations; usage is reported as CrewAI supplied it.
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
Browser writes require a separate revenueops_browser_test database and APP_ENV=test.
The sign-in helper verifies synthetic identity and test environment before every workflow.
Playwright defaults to port 5175; E2E_URL overrides it for the isolated CI service.
Use the isolated setup in docs/deployment/local.md. No test starts a paid model or sends mail.

Optional live comparison (explicit local-only invocation):
```sh
MODEL_MODE=ollama OLLAMA_URL=http://localhost:11434 PYTHONPATH=backend .venv/bin/python -m app.evaluations.runner --live
```
Ordinary CI never supplies --live. Published live artifacts are recorded local evidence,
not a claim CI ran inference. Interrupted multi-case comparisons should be rerun explicitly.


## Iteration 010 frozen comparison and sealed holdouts
The original four Iteration 009 cases and labels remain immutable. Seven new synthetic
holdouts were committed before interface changes/live inference. See
[predeclared method](iteration-010/methodology.md), [all live results](iteration-010/results.md)
and comparison.json. One attempt each, no favourable rerun selection; errors count as
incorrect, not abstention. Accepted pairs and partial recall differ from exact decisions.
Current 0/4 fixed and 1/7 holdout outcomes do not demonstrate investigation improvement.
Historical failed-run token usage is unknown; compare coverage before comparing totals.
