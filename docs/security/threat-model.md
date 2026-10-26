# Threat model and controls
Actors: anonymous callers, legitimate analysts, reviewers, other organisations, injected
CSV/reference/dispute text, compromised model outputs, failed workers and concurrent reviewers.
Assets: authoritative receivables, allocation integrity, customer information and decision history.

| Threat | Implemented boundary | Verification / remaining limit |
|---|---|---|
| Cross-organisation lookup | Every repository/API lookup scopes organisation; tools only receive scoped snapshots | API and tool isolation tests; database owner remains privileged |
| Unauthorised allocations | Current DB role checked per request, human review API, no agent write tools | Viewer/analyst denial tests |
| Replay / concurrent posting | Org and record locks, unique idempotency keys, transactional allocations | Replay tests and real PostgreSQL concurrent receipts test |
| Hallucinated evidence | Strict schema, field/value citation equality, invoice allowlist, fresh balance checks | Adversarial contract tests; free prose semantics still need human judgment |
| Prompt injection | Untrusted text policy, one allowlisted read-only tool, no delegation/write/network tools | Tool capability tests; not a guarantee a model ignores all injected prose |
| Stale worker | Leased jobs, fencing tokens, bounded child process and result checkpoint | Lease recovery and stale-token tests |
| Credential exposure | Argon2, signed expiring HttpOnly cookies, production secret validation | Login tests; no secrets returned by settings |
| CSRF / browser abuse | SameSite Strict, explicit Origin and custom mutation header, CSP at ingress | Origin/header tests; HTTPS and shared edge rate limiting required |
| Malicious uploads | UTF-8 CSV, extension/content-type/size/row/field bounds, atomic validation | Import tests; ingress enforces body bound including chunked requests |
| Export formula injection | Formula-leading references apostrophe-escaped | Export security test |
| Unapproved communication | No sender dependency, transport, API or tool exists | Draft approval remains approved_not_sent |

Roles: viewer read; analyst import/reconcile/investigate/dispute/draft; reviewer additionally
approves allocations, resolves disputes and verifies customer identities; admin same operational
rights. Operators provision accounts through a password-prompt CLI; no public registration.
Production must disable demo seed, use HTTPS, private DB networking, scoped DB credentials,
strong JWT key, managed backups, trusted ingress, and security monitoring. Local password auth
has no MFA/SSO or password-reset service yet; review before exposing to real financial data.
No sensitive data was transmitted to a hosted model. External telemetry exports disabled.
