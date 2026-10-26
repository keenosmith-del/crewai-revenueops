# Iteration 007 — CI/CD and deployment preparation
Scope: verification workflow for PostgreSQL, financial/agent/flow/security/API contracts,
frontend checks/build/browser, dependency checks, secret scan and image builds; separate
manual existing-staging deployment with independent review, exact successful main CI SHA,
registry digests/revision labels, baseline drift checks, production configuration gate,
recovery manifests, smoke and reviewed rollback. No provisioning or schema deployment.

Actual local results: API/worker and web Docker images built successfully. Official
checksum-verified actionlint 1.7.12 validates both workflows. Release guard/manifest tests:
20 passed with synthetic GitHub/host data. Backup restored into a separate database;
source and restored counts 155 invoices / 121 transactions / 2 allocations, aggregate
allocations 2629.000. No source database reset or destructive history changes.

Read-only remote inspection: zero Actions runs, zero environments. No push, registry
publish, SSH deployment, environment setup or workflow dispatch authorised/executed.
Hosted CI and CD are prepared, not live verified. Local checks do not establish cloud
identity, environment enforcement or production correctness. Deployment activation and
credentials remain explicit operator prerequisites in docs/deployment/staging.md.

Previous iteration 2a14e2b. This stage hash recorded in final release manifest.

Verified implementation commit: `cde9a4c115a26ab2bd5e2b32e977b11415044fac`.
