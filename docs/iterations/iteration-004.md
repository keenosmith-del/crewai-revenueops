# Iteration 004 — connected operational console
Scope: React Router application, shared shell/design tokens, one JSX/CSS folder per
page; dashboard, invoice details/disputes, bank import preview/confirmation/history,
reconciliation/review, investigations, customer accounts, agent executions/tools,
collections draft approval, reports export, audit, settings and sign-in.
Validation: frontend lint, 5 component tests and Vite production build passed.
Playwright: 3 passed against real local PostgreSQL/API, including persisted allocation,
CSV import, approved-but-not-sent collections draft and 390px responsive navigation.
Dependency audit after fixed-version upgrades: zero vulnerabilities.
Ports 5050/5173 occupied by existing services; used 5051/5174 without killing them.
Limitations: dense structured evidence uses JSON inspection; customer detail currently
uses bounded related-record views rather than a full CRM editor. No external sending.
Previous stage c245fe1. Hash recorded in final release manifest.
