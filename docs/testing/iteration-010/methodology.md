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

## Reproduction after implementation
Use a new absolute output directory for every live execution (existing reports are refused):
```sh
MODEL_MODE=ollama OLLAMA_URL=http://localhost:11434 OLLAMA_MODEL=llama3.2:3b PYTHONPATH=backend .venv/bin/python -m app.evaluations.investigation --live --timeout 240 --output-dir "$PWD/docs/testing/iteration-010/fixed-live-NEW"
MODEL_MODE=ollama OLLAMA_URL=http://localhost:11434 OLLAMA_MODEL=llama3.2:3b PYTHONPATH=backend .venv/bin/python -m app.evaluations.investigation --live --timeout 240 --dataset "$PWD/data/evaluations/holdout-010.json" --output-dir "$PWD/docs/testing/iteration-010/holdout-live-NEW"
```
Without --live, the default baseline smoke writes .runtime/evaluations/baseline.json;
pass a unique --output-dir to retain it as evidence. Ordinary CI runs both datasets with
no inference. Actual historical live claims require the checked-in live reports.

Pipeline-phase inference_failures includes errors raised during CrewAI, including typed
conversion errors. validation_rejections_observed counts guardrail callbacks, not every
internal provider/converter attempt. final_validation_failures counts only failures after
CrewAI returns (output or financial validation). These measures can overlap and must not
be summed as mutually exclusive totals. Error types classify failures; absent raw output
or field diagnostics cannot establish which exact model field was wrong.

Changed source_id evidence and role routing prevent attributing an effect solely to the
model or prompt. Compare same fixed labels across iterations, preserve both original 009
reports and all 010 attempts. Token usage on caught failures is partial when available;
process timeout usage is unknown. Do not compare a full-run token sum with historical
completed-only usage as an efficiency gain. Fewer calls can also mean earlier failure.

Baseline summary latency_ms=0 is an uninstrumented placeholder, not a measured zero
runtime. Latency comparisons in results.md refer only to actual assisted runs.
