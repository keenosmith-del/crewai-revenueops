# Product requirements and acceptance map
Finance analyst imports validated records and investigates exceptions. Finance reviewer
authorises allocations, resolves disputes and approves internal collection drafts. Viewer
examines records/reports. Operator manages identities, secrets, backups and deployment.

Journey: sign in → inspect per-currency dashboard → create customer accounts → preview
invoices/bank CSV → fix validation errors → confirm → run deterministic reconciliation →
inspect exact/partial/overpayment/combined/exception proposals → request CrewAI where
interpretation is needed → inspect tools and evidence → reviewer approve/reject/request
information → verify derived balances and audit → prepare an eligible overdue draft →
record approved_not_sent → export receivables and inspect evaluation evidence.

| Requirement | Implemented evidence |
|---|---|
| Validated idempotent imports | imports service, source hashes/unique IDs, preview UI, row errors |
| Persistent financial truth | PostgreSQL models, migrations, immutable allocations |
| Exact money and controls | Decimal policy, locking/validation, generated and concurrency tests |
| Practical operations | Dashboard, invoice/transaction/account detail, reconciliation/review |
| CrewAI competency | Four roles, sequential task contexts, typed Flow, BaseTool and guardrails |
| Human authority | Live-role reviewer API; no agent posting or sending tools |
| Recovery | Leased job claims, time budgets, fencing and persisted result checkpoints |
| Observable operation | HTTP correlation, audit, task outcomes, execution usage/errors and tool calls |
| Evaluation | 13-case known-truth baseline; separate mocked contracts and real local probe |
| Deployment preparation | Containers, CI workflow and separately protected existing-staging workflow |

Non-functional requirements: organisation isolation; strict schemas; bounded uploads;
no mixed-currency totals; respectful collections; explicit failures; calm responsive and
keyboard-accessible UI; no paid services required for baseline. Evidence of local checks
is in docs/testing/results.md. Production activation requires the documented authentication,
network, backup and security review. No production-readiness claim follows merely from
passing local checks.

Intentional limits: CSV only (no PDF/OCR), no live banking/payment/FX/accounting posting,
no external message sending, no SSO/MFA/password-reset service, no HA guarantee, no
statistically representative agent accuracy benchmark, no hosted CI/deployment execution.
