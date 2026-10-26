# System architecture
```mermaid
flowchart TD
    Browser[React JSX console] --> Web[Static Nginx or Vite proxy]
    Web --> API[FastAPI authenticated REST API]
    API --> Services[Import / reconciliation / review / collections services]
    Services --> PG[(PostgreSQL 17)]
    Worker[Leased PostgreSQL worker] --> PG
    Worker --> Flow[Typed CrewAI Flow]
    Flow --> Crew[Conditional specialist crew]
    Crew --> Tools[Scoped read-only evidence tool]
    Crew --> Ollama[Local Ollama via native OpenAI-compatible provider]
    Flow --> Validate[Schema / citation / financial validators]
    Validate --> PG
    API --> Human[Human approval boundary]
    Human --> Ledger[Atomic immutable allocations]
    Ledger --> PG
```
Services separate routes, request/output schemas, scoped repository access, Decimal
accounting, deterministic engine, evidence snapshots, provider configuration, CrewAI
definitions, Flows and durable workers. PostgreSQL owns business records and workflow
checkpoints. SQLite exists only in isolated unit/evaluation tests, never as business truth.
No DB transaction is held during model inference. The frontend can request actions but
cannot supply authoritative balances. No external messaging or banking integration exists.

```mermaid
sequenceDiagram
    participant User as Finance analyst
    participant API
    participant DB as PostgreSQL
    participant Worker
    participant Crew as CrewAI specialists
    participant Reviewer
    User->>API: Preview and confirm CSV
    API->>DB: Atomic validated import and audit
    User->>API: Run reconciliation
    API->>DB: Batch, conservative proposals and exceptions
    User->>API: Request investigation
    API->>DB: Durable job
    Worker->>DB: Claim lease and snapshot scoped evidence
    Note over Worker,DB: Commit and release transaction
    Worker->>Crew: Conditional investigation / dispute / collections
    Crew-->>Worker: Structured cited recommendation
    Worker->>DB: Validate, checkpoint and save recommendation
    Reviewer->>API: Approve with idempotency key
    API->>DB: Lock, revalidate, allocate and audit atomically
```

```mermaid
erDiagram
    ORGANISATION ||--o{ USER : employs
    ORGANISATION ||--o{ CUSTOMER : owns
    CUSTOMER ||--o{ INVOICE : billed
    CUSTOMER ||--o{ TRANSACTION : pays
    IMPORT ||--o{ INVOICE : provenance
    IMPORT ||--o{ TRANSACTION : provenance
    BATCH ||--o{ INVESTIGATION : creates
    TRANSACTION ||--o| INVESTIGATION : examined
    INVESTIGATION ||--o{ EXECUTION : runs
    EXECUTION ||--o{ TOOL_CALL : records
    INVESTIGATION ||--o{ REVIEW : reviewed
    INVESTIGATION ||--o{ ALLOCATION : authorises
    INVOICE ||--o{ ALLOCATION : receives
    TRANSACTION ||--o{ ALLOCATION : funds
    INVOICE ||--o{ DISPUTE : held
    INVOICE ||--o{ DRAFT : followup
    ORGANISATION ||--o{ AUDIT : traces
    ORGANISATION ||--o{ IDEMPOTENCY : deduplicates
```
Evidence references are typed structured output embedded in execution/proposal JSON;
crew/task composition is versioned YAML/Python and task outcomes are auditable events.
Normalisation is pragmatic: no redundant authoritative balance/status columns or separate
agent database. Organisations are scoped at the application boundary; PostgreSQL owner
credentials remain privileged and deployment must restrict direct access.
