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

Stage 2 commit 2a1029838a38cb9dafa2f38dbfdbf635357ce619 verified on origin/main.
Hosted run https://github.com/keenosmith-del/crewai-revenueops/actions/runs/40370217830
succeeded in all five jobs; receipt ci-stage-2.json. Local live evaluation begins only
with this frozen application configuration. No prompts or labels change between cases.

## Stage 3 — live evaluation and full verification (in progress)
Run fixed-live-01 then holdout-live-01 sequentially on installed llama3.2:3b; all attempts
retained. The added source_id changes the evidence schema relative to 009; dataset and
labels stay frozen, baseline/assisted evidence hashes match within 010. Any before/after
change is the combined interface/evidence/routing effect, not isolated model improvement.

Verification setup corrections: first Alembic invocation from repository root failed to
find migrations; repeated from required backend directory succeeded, including alembic
check. First restricted dependency audit lacked network access; authorised network rerun
found the same four reviewed Chroma advisories and no unreviewed findings. Initial secret
scan invocation targeted the tool directory; corrected invocation uses its binary.

Frontend lint, five component tests and build passed; no frontend source/design changes.
First local Playwright run: four passed, one reconciliation table wait timed out at 5s
while local inference competed for resources. Hosted browser job passed. Retain failure;
rerun after inference completes and report both outcomes, without extending assertions.

### Stage 3 observed live result and verification
Fixed: 0/4 exact, no supported pairs, four ValidationError failures, no completed task,
8/8 successful tool calls, 195097ms, 99118 reported tokens (possibly partial on failures).
Historical fixed: 0/4 exact, two completed abstentions, two failures, 30/43 successful
calls, 489037ms; only two cases have known usage (73272 tokens). Completion regressed.
Holdout: 1/7 exact vs baseline 4/7; one of three supported pairs, one valid abstention,
five ValidationError failures, 16/16 successful calls, 278824ms, 173170 reported tokens.
One split proposal recovered 80.00 but omitted the required 40.00 companion allocation.
The sole exact holdout success is safe abstention on the foreign-currency invoice case.
No timeouts, accepted wrong pairs, or ledger writes. No quality or token-efficiency gain.
Nine failures across eleven cases remain in denominators. All attempts are retained.

Full checks: 100 PostgreSQL/backend/release passed (138 warnings); deterministic 13/13;
frontend lint, 5 component tests, build and zero-vulnerability npm audit; migrations/check;
pip check; Ruff/actionlint; contracts; Gitleaks; same four reviewed Python advisories,
zero unreviewed. Stage 2 hosted logs independently show 80 backend + 20 release + 5
frontend + 5 browser passed; both containers built. Protected financial/security/worker,
frontend, deployment and original benchmark/report files unchanged (safety-review.json).

Local browser initial 4/5 retained. Rerun after inference: 5/5 in 11.8s on the same
synthetic DB, with warmed services and cases already generated; first failure cause is
not uniquely established. No assertions/timeouts/frontend implementation changed. Isolated
API/frontend stopped; only this iteration's disposable browser DB removed and the db
service started for verification stopped. Existing data volumes and databases preserved.

README, agent engineering, methodology, results, portfolio/handover and release manifest
updated with failures and limits. Stronger-model comparison unperformed: none installed;
no download, paid model, deployment, paid provisioning, bank action or communication.
Full-schema guidance did not resolve typed output and adds prompt text. A future
investigation needs field-level error metadata and controlled stronger-model evaluation;
no guardrail should be loosened. Stage 3 hosted outcome will be recorded after observation.
