# Iteration 009 — hosted CI correction, investigation evaluation and documentation sync

## Scope and authorised boundaries
Focused stages: (1) repair and verify hosted CI, (2) ambiguous-case evaluation and financial
safety checks, (3) synchronise release documentation with verified remote outcomes.
The user explicitly authorised normal commits/pushes to the existing origin/main throughout
this iteration. No deployment, infrastructure provisioning, paid model or AssessFlow change.
The same staged verification and truthful evidence requirements apply to future iterations.

## Starting state and reproduced failure
Local and origin/main both at ccd52b98f1a6de0559e3281afafe03370c000513, clean working tree.
GitHub run https://github.com/keenosmith-del/crewai-revenueops/actions/runs/40349229404 failed
backend/browser container initialisation: single-quoted health command was split, exposing
-U to Docker's option parser. Prior locally verified stages were already pushed by the
user; the old release documents describe their earlier local-only verification snapshot.

## Stage 1 — PostgreSQL service initialisation correction (verified)
Both service options now use folded YAML and a double-quoted health command, including
the explicit database name, 3s interval, 5s timeout and 20 retries. Application code unchanged.
Local validation and actual pushed commit/run outcome will be appended after execution.
A commit cannot record its own hash or a future hosted conclusion; the next evidence
commit records those observed facts. No hosted success is claimed in advance.

## Stage 2 — ambiguous investigation evaluation (verified)
Use identical evidence and independently specified ground truth for baseline and assisted
runs. Require actual local inference for live claims; retain errors, tool calls and latency.
Keep all evaluation data synthetic and all agent tools read-only. No financial posting.

## Stage 3 — documentation and final release state (local checks; hosted verification follows push)
Update README, results, handover, engineering summary and release manifest with observed
remote history and successful hosted verification. Final working tree must be clean and
intended commits on remote main, with a successful verification run on the final SHA.

### Stage 1 local checks before first push
- Official actionlint 1.7.12: both workflows passed.
- git diff --check: passed; reviewed only workflow quoting, persistent stage-delivery
  conventions and this iteration record.
- Initial hosted run inspected: backend/browser failed initialisation; frontend,
  container builds and secrets jobs passed. No initial hosted success claimed.

### Stage 1 verified remote result
- Commit: `9bacbe4f4a04d279477e891b5edbd62bff9ebd11`.
- Normal push to origin/main verified by git ls-remote: exact matching SHA.
- Hosted run: https://github.com/keenosmith-del/crewai-revenueops/actions/runs/40350394359
- Conclusion: **success**; backend, browser, frontend, containers and secrets all passed.
- Both PostgreSQL services initialised correctly. No subsequent CI failure in this stage.
- Existing focused PostgreSQL financial/security/import/idempotency/agent/worker tests:
  **57 passed**, 113 compatibility warnings, 7.77s.
- Dependency recheck: same four reviewed Chroma server advisories; zero new/unreviewed
  findings. Exceptions and their 2026-11-26 expiry were not broadened or extended.

### Stage 2 checks and method (live run completed)
- Added four frozen, labelled ambiguous cases: alias/remittance, competing invoice pairs,
  conflicting dispute/remittance and insufficient/injected evidence.
- Same source fixture and hashed snapshot for baseline and actual Flow; ground-truth
  labels excluded from model context. No operational DB or financial posting.
- Baseline exact labelled decision accuracy: **1/4**; three abstentions, one semantically
  wrong-target proposal (financial-policy-valid, never posted). This is not the earlier
  easy-abstention benchmark and not a claim of unsafe automatic ledger behaviour.
- Evaluation tests: **10 passed** (including original regression test), 37 framework
  warnings, 3.75s. Expanded full PostgreSQL/release suite: **87 passed**, 149 compatibility
  warnings, 21.44s. Ruff/actionlint passed. Ordinary CI adds baseline smoke only.
- Actual local run uses the unchanged application CrewAI/Flow/guardrails and Ollama
  llama3.2:3b, one attempt per case, 240s ceiling. Final results will be recorded after all
  cases finish; failures remain in the denominator. No improvement is assumed.

### Stage 2 observed live outcomes before push
- Four fixed cases, one attempt each; same dataset/runner and per-case evidence hashes verified.
- Baseline **1/4** exact decisions; assisted **0/4**. Both supported matches were missed by
  abstention, one case timed out at 240s, one failed with a generic Exception during inference.
- Tool calls/latency: alias 8 / 72430ms; combinations 13 / 61237ms; dispute 5 / 240047ms;
  insufficient evidence 17 / 115323ms. Total 43 calls and 489037ms. No ledger allocations.
- No improvement claim: the harder cases expose model limitations. Assisted precision
  undefined because no accepted allocations; both approaches recovered zero labelled matches.
- Exact model digest/runtime/application hashes and concise results retained in
  docs/testing/iteration-009. No agent prompt, model, guardrail or financial policy tuned.
- Stage 1 hosted logs additionally confirm 58 backend tests, 20 release tests, 5 frontend
  tests and 5 browser workflows passed; zero unreviewed dependency findings.

### Stage 2 verified remote result
- Commit: `8d48c26ac1e351a4357a012f3893a7e2e06a208e`.
- Verified exact SHA on origin/main by ls-remote and GitHub commits/main API.
- Hosted run: https://github.com/keenosmith-del/crewai-revenueops/actions/runs/40354134960
- **Success**, all five required jobs. Hosted tests: **67 backend passed** (149 warnings,
  9.75s), **20 release passed** (0.12s), **5 frontend passed**, **5 browser passed** (24.4s).
- Baseline smoke for all four new cases, migrations, lint/format, contracts, advisory
  policy, secrets and both container builds passed. Live inference was local only, not CI.

### Stage 3 documentation checks before push
README, results, handover, portfolio engineering and manifest now reflect pushed/verified
CI rather than the earlier local-only snapshot. Historical 81% coverage is explicitly
labelled Iteration 008. Four-case 0/4 model results qualify the earlier easy 3/3 probes.
Current staging guide/demo wording is synchronised: CI verified, deployment unexecuted.
Read-only remote checks found zero deploy-staging.yml runs and zero environments.
Exact final documentation SHA/run will be recorded after actual push and hosted success.
No self-referential commit hash or predicted future success is claimed.
