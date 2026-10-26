# Actual verification results — 2026-10-26

| Check | Actual outcome |
|---|---|
| Final PostgreSQL suite | **78 passed** (58 backend/financial/agent/worker/security/evaluation checks + 20 release checks), 113 framework/deprecation warnings; 57.34s |
| Backend statement coverage | **81%** (1,290 statements); financial workflows 93%, matching engine 94%, imports 81%, worker 68% |
| Ruff lint and format | Passed for backend, scripts and release tests |
| Frontend lint | Passed |
| Frontend components | **5 passed** |
| Frontend production build | Passed, Vite 7.3.7 |
| Playwright | **5 passed**, 14.7s; real API/PostgreSQL in a dedicated disposable test database |
| Migration upgrade/check | Clean database upgrade applied; current schema reports no new operations |
| Dependency consistency | Host and production API image pip check passed |
| Frontend vulnerability audit | Zero vulnerabilities at verification time |
| Python advisory check | Four documented Chroma server advisories remain; zero unreviewed findings; expiring exception review |
| Secret scan | Official checksum-verified Gitleaks scanned committed history: no leaks; final scan rerun after engineering commit |
| Workflow validation | Official checksum-verified actionlint **1.7.12**, both workflows passed |
| Container builds | Production API/worker and web images built successfully on local arm64 Docker |
| Container runtime | PostgreSQL, API, worker and Nginx web running; API health and database connectivity passed |
| Browser/API smoke on production images | Web 200 + CSP, health OK, anonymous identity 401, synthetic authenticated reads, Decimal strings, evaluation route 200 |
| Backup/restore | Separate restored DB matched source: 155 invoices, 121 transactions, 2 allocations, total allocations 2629.000 |
| Hosted GitHub Actions | **Not executed**; read-only inspection found zero runs |
| GitHub staging environment | **Not configured**; read-only inspection found zero environments |
| Registry publish / deployment / production | **Not executed** |

Coverage includes automated tests only; real model subprocesses and browser execution
are not folded into that percentage. Uncovered provider/worker process supervision and
operator CLI paths remain review areas. Warnings come mainly from installed CrewAI
compatibility internals and Starlette's current httpx TestClient deprecation; they are
recorded rather than suppressed or represented as application failures.

## Financial evaluation
13 independently labelled synthetic cases: 13/13 classifications, 13/13 exact proposed
allocation sets, proposal precision 1.0 and recall 1.0. The benchmark is deliberately
small and constructed; these figures are regression evidence, not field accuracy.
The separate original 150-invoice/120-transaction seed has exact expected outcomes in
data/synthetic/expected-outcomes.json. No seed proposals post automatically.

## Genuine local model evidence
- Initial larger case: TimeoutError, 1 recorded tool call, no completed recommendation.
- Small persisted case: two-agent crew completed in **31,883ms**, 2 tool calls, result
  request_information at human_review; no allocations. CrewAI reported 13,656 tokens;
  some token accounting can be approximated by the framework, not independently metered.
- Same-case comparison: unmatched, cross-currency and injected-reference cases all
  completed with live local crews. **Baseline 3/3, assisted 3/3**, no failures, 3 tool calls
  each. Durations 55,418ms / 62,210ms / 60,260ms. Correct means no unsupported allocation
  and request_information/escalate. This does not prove an improvement or general model safety.
- Larger main-workspace native-adapter retry: ValidationError after **147,763ms** and
  23 tool calls. Persisted as failure, no proposal or financial state change.

Exact structured artifacts: live-model.json, live-small-model.json,
live-comparison.json and live-main-model.json. No hosted model was invoked. Small live
success and larger-case failures must both be disclosed during a demonstration.

## Browser and visual evidence
Five workflows verify persisted review/allocation, invoice and transaction CSV imports,
explicit baseline not_executed status, correct changed balances, approved_not_sent drafts,
audit, all operational routes and customer history, and 390px reduced-motion navigation.
Tests assert synthetic identity and APP_ENV=test before writes. They use the separate
revenueops_browser_test database and signing key. The ordinary demo ledger is independent.
Screenshots in evidence/ were visually inspected; final mobile capture waits for closed
navigation and loaded data. No accessibility compliance certification or load test is claimed.

## Reproduction and truthful boundaries
Commands in methodology.md and deployment/local.md reproduce the checks. Test fixtures
never call a paid provider. Mocked contract tests genuinely execute CrewAI orchestration,
but mocked inference is not live inference. Local arm64 images do not establish hosted
linux/amd64 builds or staging correctness. No push, remote environment activation,
external messaging, payment execution or paid infrastructure provisioning occurred.
