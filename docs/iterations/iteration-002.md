# Iteration 002 — financial persistence and reconciliation
Scope: normalised SQLAlchemy records, initial Alembic schema, Decimal policies, CSV
preview/confirmation, source hashes, duplicates, deterministic match classifications,
repeatable 150-invoice/120-transaction synthetic seed.
Tests: 13 pytest checks passed locally (including generated cents); real PostgreSQL
migration applied and Alembic check reports no drift. Separate PostgreSQL test run
recorded in final results. Seed is synthetic, opt-in outside production.
Decision: conservative review for all proposals; unsupported FX and unknown accounts
fail closed. No authoritative balance stored separately from allocations.
Limitations: CSV only; PDF extraction/OCR intentionally not claimed.
Previous stage: 1be4525. This commit hash is in the release manifest.
