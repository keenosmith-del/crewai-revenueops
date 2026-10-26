# Iteration 006 — evaluation and security
Scope: 13-case deterministic benchmark, organisation-scoped evidence security,
PostgreSQL concurrent approvals, production configuration gates, safe exports, customer
provision/verification controls, request correlation, accessible allocation form, actual
local-model probes and explicit dependency advisory review.
Actual results: 51 passed/1 PostgreSQL-only skip on SQLite; PostgreSQL results in final
results.md. Baseline 13/13 classification and allocation cases; proposal precision/recall
1.0 on this deliberately small synthetic regression set, not a production accuracy claim.
Ollama larger case timed out; smaller persisted case completed in 31,883ms with 2 tool
calls and 13,656 reported tokens. No ledger mutation. No paid model calls.
Dependency audit: zero frontend vulnerabilities. Python has 4 unpatched Chroma server
advisories; exact expiring exceptions document why no affected server path is exposed.
Removed optional LiteLLM and unused AWS dependencies; native OpenAI-compatible Ollama
provider allows patched filelock 4.2.1 without breaking supported dependency constraints.
Tests actually invoke CrewAI with mocked inference; do not confuse with the live probe.
Previous iteration 823ccff. This stage hash in final release manifest.
