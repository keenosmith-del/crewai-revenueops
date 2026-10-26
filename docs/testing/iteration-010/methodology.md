# Iteration 010 predeclared evaluation

Keep data/evaluations/ambiguous-cases.json (four cases) and Iteration 009 reports immutable.
Use seven separately labelled cases in holdout-010.json, sealed before interface changes.
Holdouts are hand-authored, not a representative or statistically independent population.
Labels never enter the evidence snapshot or task. No label changes after live evaluation.

Run one sequential attempt per case/configuration, temperature zero, 240s outer ceiling.
Include all failures in exact accuracy; do not count errors as safe abstentions. Report
accepted exact allocation pairs recovered, wrong pairs, abstentions, tool statuses,
observed guardrail failures, inference failures, latency and available framework token
usage. Unknown/partial failed-run tokens remain unknown. Compare frozen four cases with
009; report holdout separately, with no historical holdout improvement claim.

SQLite isolates synthetic evaluation; PostgreSQL tests separately verify financial locking
and operational controls. Every proposed allocation passes existing financial validation.
No ledger posting or external communications. Cross-currency evidence stays excluded by
the existing service; agents cannot perform FX. Preserve proposal attempts if rejected.

CrewAI 1.15.30 supported practices reviewed 2026-10-26:
- https://docs.crewai.com/v1.15.30/en/concepts/tasks (typed output, explicit context, callable guardrails)
- https://docs.crewai.com/v1.15.30/en/concepts/tools (BaseTool with typed args_schema)
- https://docs.crewai.com/v1.15.30/en/concepts/agents (bounded iterations and execution)
Validate actual installed API and behaviour with contract tests; no framework upgrade.

Local inventory: Apple Silicon, 16 GiB RAM; only llama3.2:3b Q4_K_M (~2.02GB) installed.
No stronger local candidate is available. No download, paid provider or resource provisioning
is needed to test interface reliability. A stronger-model comparison remains unperformed.
