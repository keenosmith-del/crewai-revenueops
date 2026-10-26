# Operations and recovery
/health verifies database reachability. Structured HTTP logs include correlation ID,
method/path/status/duration, not request bodies or secrets. Audit records include actor,
record, transitions and matching request correlation. Agent Workspace exposes execution
mode/model/stage/attempts/usage/result/error and scoped tool invocation timing. Report
metrics are derived from database records, per currency; they are not fabricated counters.

Worker restart: stop the affected worker; unexpired leases prevent simultaneous ownership.
After 90s expiry another worker may claim; stale fencing tokens cannot save outputs.
A child is bounded to 480s and agent budget to 180s; three expired claims exhaust retries.
A failed case can be explicitly requeued from the UI/API. Completed validated result
checkpoints skip inference on a reclaimed execution. Incomplete read-only inference may
repeat. Workers never record allocations, so restart cannot replay a financial posting.

Imports: previews with row errors cannot confirm. Correct and re-upload the source; exact
hash+mapping reimports return the same record. Concurrent source IDs are protected by
unique constraints and organisation-level confirmation lock. No partial file commits.
A conflict rolls back the transaction; do not directly edit ledger rows to bypass it.

Finance incidents: stop approval traffic, preserve audit and database backup, identify
correlation/record IDs, compare allocations to source evidence and obtain a reviewer
resolution. No refund, credit note or destructive history rewrite endpoint is provided.
Collection approval never sends. Investigation errors do not alter balances.

## Backup and restore exercise
Use a project-local protected backup directory (not committed); backups contain financial
data and must be encrypted/access-controlled in a real environment. Example local demo:
```sh
mkdir -p .backups
docker exec revenueops-db-1 pg_dump -U revenueops -Fc revenueops > .backups/revenueops.dump
docker exec revenueops-db-1 createdb -U revenueops revenueops_restore_test
docker exec -i revenueops-db-1 pg_restore -U revenueops -d revenueops_restore_test --exit-on-error < .backups/revenueops.dump
```
Compare table counts, allocation totals and Alembic revision. Only remove the disposable
restore database after confirming it is not the source. Scheduled encrypted backups,
retention, off-host recovery and RPO/RTO monitoring remain infrastructure prerequisites.
Do not treat container-volume persistence as a backup or run pg_restore against production
without an explicitly approved incident plan. The implementation's actual restore result
is recorded in docs/testing/results.md.
