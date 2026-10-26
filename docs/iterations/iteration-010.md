# Iteration 010 — CrewAI investigation reliability and quality

Authorised scope: repository-only staged commits and pushes; no deployment, paid inference,
provisioning, payments or communications. Starting main: 72b4f6b (Iteration 009 receipt).
Frontend implementation and financial posting controls remain outside the change scope.

## Stage 1 — failure audit and sealed evaluation design
Original four cases and labels remain byte-for-byte unchanged. Seven separate synthetic
holdout cases are sealed before implementation or live inference: supported single intent,
split allocation, ambiguous intent, open dispute, absent linkage, hostile note and foreign
currency. One attempt per case per configuration, failures retained, no favourable reruns.

Audit: 43 calls, 30 successful and 13 not_found; doubled prefixes and business references
confused with IDs. Both completed cases abstained despite remittance facts, requesting
transaction data already present. Actual source_id was omitted from the snapshot despite
remittance notes naming it. Failure records contain one timeout and one generic inference
Exception; they do NOT prove a structured-output validation failure count. Failed runs
have unavailable usage, not zero. Completed runs report 73,272 tokens. See failure-audit.json.

Stage 2 will clarify IDs/errors and evidence semantics, reduce repeated work, retain
independent review and exact citation validation, and instrument validation failures.
Stage 3 will run frozen and holdout evaluation plus full verification and publish honest
results. Final receipt records preceding observed SHAs/runs; its own receipt is reported
externally because a commit cannot contain its own hash.

Stage 1 local verification: Ruff passed; existing evaluation tests 10 passed (37 framework
warnings); diff check passed. No application changes in this stage. Hosted outcome pending.

Stage 1 commit f1e21382a9ec686eb585d7ca93021a2f66f64244 verified on origin/main.
Hosted run https://github.com/keenosmith-del/crewai-revenueops/actions/runs/40369553647
succeeded: backend, browser, frontend, containers, secrets (receipt ci-stage-1.json).

## Stage 2 — interface and evaluation reliability
Added one scoped snapshot read, explicit raw ID/citation distinction, allowlisted error
hints and single matching-prefix handling. Added missing source_id evidence. Prompts state
resolved vs open dispute semantics and require concrete missing information. Ordinary
ambiguity uses investigator + independent quality reviewer; actual open disputes retain
three roles. All typed findings and exact-citation/financial controls remain enforced.
Supported CrewAI APIs retained: BaseTool args_schema, sequential explicit context,
output_pydantic, callable guardrail and bounded retry. No framework dependency changes.

Runner adds separate holdouts, guarded unique live report directories, hashes of application
files, observed validation events, partial available usage on exception, proposal capture
before financial rejection, tool success and failure metrics. Historical 009 reports cannot
be overwritten by defaults. Financial SQL and ledger mutation code unchanged.

Initial verification exposed two test expectations needing update: Flow copies context
(the routing test must mutate flow.context), and security allowlist now includes snapshot.
Neither required weakening a guardrail. SQLite run initially 98 passed, 1 failed, 1 skipped
before correcting the tool-kind expectation; definitive PostgreSQL results follow.

Stage 2 definitive local checks: 100 backend/release tests passed against real dedicated
PostgreSQL (138 compatibility warnings, 8.03s); Ruff lint/format, actionlint and diff check
passed. Fixed baseline 1/4, holdout baseline 4/7; zero labelled supported allocations
recovered by either baseline. No live inference results yet. Hosted outcome pending.
