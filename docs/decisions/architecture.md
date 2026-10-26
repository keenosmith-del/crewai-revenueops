# Architecture decisions

## ADR 001 — CrewAI with a deterministic financial core
Accepted. CrewAI interprets unclear references, coordinates independent specialist
review and prepares concise findings. Ordinary software is better at exact money,
matching, permissions, idempotency and posting. Agents have no financial mutation tools.
Rejected: an LLM ledger, agent agreement as evidence, or a chatbot-only demonstration.

## ADR 002 — PostgreSQL and application-owned checkpoints
Accepted. Numeric arithmetic, uniqueness and transactional row locks protect allocation
invariants; SKIP LOCKED claims avoid a broker. Execution JSON checkpoints integrate with
the same business transaction boundary. Rejected: authoritative SQLite Flow storage and
a second contradictory workflow database. Incomplete read-only AI work can repeat safely.
No Redis/Celery, vector service or cloud tracing is needed for this scope.

## ADR 003 — Human review for every allocation
Accepted. Even deterministic exact proposals wait for an authenticated reviewer. Fresh
records are revalidated under locks, then allocation/review/audit/idempotency are atomic.
Collections drafts similarly require review and remain unsent. Automatic exact posting
was rejected as unnecessary financial risk for the demonstration policy.

## ADR 004 — React JSX, plain CSS and native Fetch
Accepted to preserve established AssessFlow page conventions and a calm editorial UI.
Vite and React Router provide purposeful tooling. No Axios, Tailwind or component suite.
FastAPI/Pydantic define explicit request contracts; SQLAlchemy/Alembic own persistence.

## ADR 005 — Native local model provider
Initial supported LiteLLM Ollama adapter was exercised but a larger case timed out.
Security review found its filelock<4 constraint prevented a patched dependency. Switched
to CrewAI's native OpenAI provider against Ollama's officially documented local /v1
compatibility endpoint. No API credits or OpenAI account needed; a small real two-agent
case completed. Hosted native OpenAI mode remains opt-in and untested. ChromaDB remains
a CrewAI transitive import with unused server advisories documented, expiring review.

## ADR 006 — Existing-VM staging promotion
Accepted as a simple cost-conscious preparation target, not a claim of production scale.
Protected manual dispatch, exact successful CI SHA, actual independent approval, pinned
host identity, image digests/revision labels, drift detection and recovery manifest mirror
AssessFlow's release-safety principles without adopting its Azure-specific architecture.
No provisioned infrastructure or active credentials; no deployment has occurred.
