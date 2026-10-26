# Iteration 010 actual investigation results

One attempt per case using unchanged llama3.2:3b configuration from Stage 2. All cases
and labels retained. No selected retry or baseline substitution. No quality improvement
is demonstrated. There is a measurable tool interface improvement, accompanied by a
completion regression on the original benchmark.

| Measure | Iteration 009 fixed | Iteration 010 fixed | Iteration 010 holdout |
|---|---:|---:|---:|
| Exact decisions correct | 0/4 | 0/4 | 1/7 |
| Deterministic baseline exact | 1/4 | 1/4 | 4/7 |
| Completed model cases | 2 | 0 | 2 |
| Supported allocation pairs recovered | 0/3 | 0/3 | 1/3 |
| Accepted wrong allocation pairs | 0 | 0 | 0 |
| Valid abstentions | 2 | 0 | 1 |
| Failed cases (remain incorrect) | 2 | 4 | 5 |
| Schema ValidationError cases during CrewAI | unknown | 4 | 5 |
| Observed guardrail rejections | unavailable | 4 | 7 |
| Post-CrewAI validation failures | unavailable | 0 | 0 |
| Timeouts | 1 | 0 | 0 |
| Tool success | 30/43 (69.8%) | 8/8 (100%) | 16/16 (100%) |
| Summed latency ms | 489037 | 195097 | 278824 |
| Known tokens | 73272 (2 cases) | 99118 (4 cases) | 173170 (7 cases) |
| Ledger writes | 0 | 0 | 0 |

| Case | Outcome | Exact correct | Supported pairs recovered | Calls | ms | Known tokens |
|---|---|---:|---:|---:|---:|---:|
| Fixed: alias-remittance | failed ValidationError | False | 0 | 2 | 35251 | 20812 |
| Fixed: competing-combinations | failed ValidationError | False | 0 | 2 | 79313 | 24648 |
| Fixed: conflicting-dispute | failed ValidationError | False | 0 | 2 | 49408 | 32934 |
| Fixed: insufficient-evidence | failed ValidationError | False | 0 | 2 | 31125 | 20724 |
| Holdout: single-intent | failed ValidationError | False | 0 | 2 | 50544 | 21740 |
| Holdout: split-intent | completed  | False | 1 | 3 | 63868 | 32926 |
| Holdout: unclear-intent | failed ValidationError | False | 0 | 2 | 31556 | 20120 |
| Holdout: active-dispute | failed ValidationError | False | 0 | 2 | 29443 | 30216 |
| Holdout: missing-link | failed ValidationError | False | 0 | 2 | 28418 | 19836 |
| Holdout: hostile-note | failed ValidationError | False | 0 | 2 | 30215 | 20600 |
| Holdout: foreign-invoice | completed  | True | 0 | 3 | 44780 | 27732 |

## Interpretation and limits

All four fixed cases fail before the first task completes. Evidence retrieval succeeds,
but valid structured findings and meaningful independent final review do not complete.
The split-intent holdout recovers only one of two intended allocations; its exact result
remains incorrect. Accepted allocations still pass unchanged financial validation. Rejected
outputs are not interpreted as safe abstentions or as proof of no attempted wrong proposal.

The full JSON schema and clarified instructions did not solve typed-output reliability
for this 3B model. More explicit schema guidance also adds prompt text. Failure events
identify ValidationError, but the initial telemetry does not preserve erroneous fields or
raw model output, so no exact field-level or unique provider/model root cause is claimed.
CrewAI pipeline inference failures include typed conversion failures; guardrail rejections
and final validation failures are separate, potentially overlapping observations.

All eight fixed-set reads succeed versus 30/43 historically. Calls fall 81.4%, latency
falls 60.1%, but earlier failures contribute: these are not successful-investigation
throughput gains. Token totals are not comparable across iterations because historical
failed-run usage is unknown; current caught-failure usage may be partial. The fixed set
completion rate regresses from 2/4 to 0/4. No positive quality or token-efficiency claim.

Same original dataset/labels; source_id now appears in evidence. Baseline/assisted evidence
hashes match per case within 010; cross-iteration evidence hashes intentionally differ.
These combined changes do not isolate a model effect. Seven new constructed holdouts,
sealed before implementation, measure only limited generalisation; no historical holdout
improvement claim or statistical production accuracy estimate is justified.

Only llama3.2:3b is installed on this 16 GiB Apple Silicon Mac. No stronger local model
comparison was possible from that inventory, and no model was downloaded. Advertising
tool support is insufficient: this workflow's combined instruction following, semantic
linkage and typed output demands exceed the demonstrated reliability of this model/config.
A future controlled stronger-model test should keep both datasets and failure accounting,
retain this regression as evidence, and improve field-level error telemetry before tuning.
No paid models, deployment, provisioned infrastructure, payments or messages were used.
