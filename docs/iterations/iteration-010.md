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
