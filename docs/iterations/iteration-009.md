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

## Stage 1 — PostgreSQL service initialisation correction (in verification)
Both service options now use folded YAML and a double-quoted health command, including
the explicit database name, 3s interval, 5s timeout and 20 retries. Application code unchanged.
Local validation and actual pushed commit/run outcome will be appended after execution.
A commit cannot record its own hash or a future hosted conclusion; the next evidence
commit records those observed facts. No hosted success is claimed in advance.

## Stage 2 — ambiguous investigation evaluation (pending)
Use identical evidence and independently specified ground truth for baseline and assisted
runs. Require actual local inference for live claims; retain errors, tool calls and latency.
Keep all evaluation data synthetic and all agent tools read-only. No financial posting.

## Stage 3 — documentation and final release state (pending)
Update README, results, handover, engineering summary and release manifest with observed
remote history and successful hosted verification. Final working tree must be clean and
intended commits on remote main, with a successful verification run on the final SHA.

### Stage 1 local checks before first push
- Official actionlint 1.7.12: both workflows passed.
- git diff --check: passed; reviewed only workflow quoting, persistent stage-delivery
  conventions and this iteration record.
- Initial hosted run inspected: backend/browser failed initialisation; frontend,
  container builds and secrets jobs passed. No initial hosted success claimed.
