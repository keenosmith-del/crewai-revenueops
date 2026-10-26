# API and authorisation
OpenAPI at /openapi.json is generated from the actual FastAPI routes. /docs exposes
interactive documentation. /health checks database reachability. API prefix /api.

Sign in POST /auth/login with email/password; HttpOnly SameSite=Strict four-hour JWT
cookie. Secure cookies required in production; bearer tokens accepted for local tooling.
No demo identity headers. Users, current role/active state and organisation are reloaded
from the DB on every request. Cookie mutations require X-Requested-With: RevenueOps;
Origins must be explicitly allowed. API returns 401/403/404/409/422 for unauthenticated,
forbidden, unavailable, state/uniqueness conflict and invalid inputs respectively.

GET resource lists accept q/status/currency/page/page_size/sort/direction. Max page 200.
POST /imports/{invoices|transactions}/preview accepts multipart CSV + mapping JSON.
POST /imports/{id}/confirm commits only an error-free preview, atomically.
POST /reconciliation builds conservative proposals, no ledger effects.
POST /investigations/{id}/review requires Idempotency-Key and decision/note; optional
allocations contain invoice_id and amount as decimal string. Approve/reject/request_information.
POST /investigations/{id}/run queues durable AI work; baseline records not_executed.
POST /invoices/{id}/disputes and /disputes/{id}/resolve manage explicit dispute holds.
POST /collections/drafts and /collections/drafts/{id}/review create/review internal drafts.
There is no sending endpoint. GET /reports/export sanitises formula-leading references.

Viewer: read. Analyst: import/reconcile/investigate/dispute/draft. Reviewer: all analyst
operations plus allocations/dispute resolution/draft approval. Admin: same operational
permissions; identity provisioning is a controlled operator command, not a public API.
No model configuration secrets or password hashes returned. Rate limiting is in-process
for local use; production requires a shared ingress rate limiter and HTTPS.
