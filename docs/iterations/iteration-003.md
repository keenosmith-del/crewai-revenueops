# Iteration 003 — authorised business workflows
Scope: authenticated API, live-role RBAC, organisation-scoped records, import/reconcile
routes, review decisions and idempotent atomic allocations, disputes, collections draft
lifecycle, reports and read-only audit. Cookie CSRF/origin controls and login limiting.
Tests: 31 backend tests passed, including approval replay, no-op rejects, currency,
customer, disputed/duplicate/over-allocation controls, API contracts, role and tenant isolation.
No message sender or payment executor exists. Production rejects demo and default secrets.
Previous iteration commit: 68bbb1e. This stage hash is in the release manifest.
Limitations: no SSO or self-service identity administration; ingress controls remain an
operator prerequisite. SQLite tests do not establish concurrency; PostgreSQL follows.

Verified implementation commit: `c245fe18871c8aa31298a148e296d79786050e51`.
