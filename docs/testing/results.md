# Actual verification results — 2026-10-26

Current Iteration 010: **100 PostgreSQL/backend/release tests passed**, 138 warnings;
frontend lint, 5 component tests and build passed. All five hosted jobs passed for
[results stage c525294](https://github.com/keenosmith-del/crewai-revenueops/actions/runs/40372045437).

[Iteration 010 complete live results](iteration-010/results.md): original fixed cases
**0/4** exact (baseline 1/4), separate sealed holdouts **1/7** (baseline 4/7). Nine typed
failures in eleven cases, one of six supported allocation pairs recovered, 24/24 successful
read calls, no ledger writes. Tool reliability improves but investigation quality does not.
Fixed-case completion regresses 2/4 to 0/4; no token-efficiency claim. The tables below are
historical Iteration 009 evidence, retained unchanged in scope.

| Check | Actual outcome |
|---|---|
| PostgreSQL/full suite, Iteration 009 | **87 passed**, 149 compatibility warnings, 21.44s locally; same 67 backend + 20 release checks passed on hosted CI |
| Focused financial/security/agent/worker checks | **57 passed**, 113 warnings, 7.77s on real PostgreSQL |
| Evaluation tests | **10 passed**, 37 warnings, 3.75s; actual Flow with explicitly mocked contract inference included |
| Last measured coverage (Iteration 008) | **81%** over 1,290 statements at that revision; not a newly measured Iteration 009 coverage claim |
| Ruff lint / format and actionlint 1.7.12 | Passed locally and in the applicable hosted steps |
| Frontend lint / components / production build | Passed on GitHub; **5 component tests** |
| Playwright | **5 passed** on GitHub against its isolated PostgreSQL service |
| Migration upgrade/check and pip check | Passed on GitHub |
| Frontend vulnerability audit | Zero vulnerabilities in the hosted audit |
| Python advisory check | Same four exact-version Chroma server exceptions, no new/unreviewed findings; expiry remains 2026-11-26 |
| Secret scan | Hosted Gitleaks job passed |
| Container builds | API/worker and web images built successfully on hosted Ubuntu/linux-amd64; no registry publish |
| Hosted Stage 1 CI | **All five jobs passed**, 9bacbe4f4a04d279477e891b5edbd62bff9ebd11, [run 40350394359](https://github.com/keenosmith-del/crewai-revenueops/actions/runs/40350394359) |
| Hosted Stage 2 CI | **All five jobs passed**, 8d48c26ac1e351a4357a012f3893a7e2e06a208e, [run 40354134960](https://github.com/keenosmith-del/crewai-revenueops/actions/runs/40354134960) |
| Hosted documentation-stage CI | **All five jobs passed**, 4c78151ef9cb043026403d0371d1d7e163dcd062, [run 40355395067](https://github.com/keenosmith-del/crewai-revenueops/actions/runs/40355395067) |
| Initial failed hosted run | [40349229404](https://github.com/keenosmith-del/crewai-revenueops/actions/runs/40349229404): PostgreSQL health command quoting split -U into Docker arguments; corrected in Stage 1 |
| GitHub environment / deploy workflow | No environment configured; zero deploy-staging.yml runs at Iteration 009 inspection |
| Registry publish / staging / production | **Not executed** |
| Earlier local runtime/restore evidence (Iteration 008) | Production images served synthetic authenticated reads; restored financial counts 155 invoices / 121 transactions / 2 allocations, aggregate 2629.000; not repeated or rebuilt in this focused iteration |

The historical coverage measurement includes automated tests only; real model subprocesses and browser execution
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

## Iteration 009 harder investigation benchmark
Four frozen synthetic cases require remittance interpretation or recognising conflicting/
insufficient evidence. Labels are excluded from prompts; per-case evidence hashes match.
Baseline **1/4** exact decisions, assisted **0/4**. Two supported matches were missed by
abstention, one case timed out at 240s and one failed with a generic Exception during
CrewAI inference. All failures count against accuracy. Actual read-tool calls **43**, summed
measured case latency **489037ms**. Both approaches recovered zero supported allocation
sets; assisted precision is undefined because no accepted allocation output was produced.
No ledger allocation or communication occurred. The financial-policy validator remains
independent of the model and rejected outputs are not silently replaced.

Per-case calls / latency: alias 8 / 72430ms; combinations 13 / 61237ms; conflicting dispute
5 / 240047ms; insufficient/injected evidence 17 / 115323ms. Exact model digest, environment,
findings, partial task events and method are in [iteration-009](iteration-009/methodology.md).
One run of four hand-authored cases cannot establish representative accuracy; these results
show no improvement and substantially qualify the earlier easy-abstention successes.

## Earlier genuine local model evidence (Iteration 008)
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
successes, larger-case failures and the harder Iteration 009 failures must all be disclosed.

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
but mocked inference is not live inference. Hosted linux/amd64 builds and push CI are now
verified by the linked runs. Neither those builds nor local checks establish staging or
production correctness. No deployment/environment activation, external messaging, payment
execution, paid model or paid infrastructure provisioning occurred. Earlier local-only
statements were the Iteration 008 snapshot, superseded by this observed pushed CI state.
