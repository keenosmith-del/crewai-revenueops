# Iteration 005 — CrewAI and durable orchestration
Scope: four configured roles, conditional sequential crews, structured task outputs,
read-only scoped BaseTool, deterministic guardrails, typed Flow and application-owned
PostgreSQL checkpoints, fenced leased jobs, child-process timeout, provider health.
Validation: all 45 backend tests passed locally, including 10 genuine CrewAI contract
checks with mocked inference and 4 job lifecycle checks. Exact Flow routing actually
executed. Ollama health verified installed llama3.2:3b advertises completion/tools.
Live local investigation launched; its actual outcome belongs in final results, not the
mocked contract-test claim. No hosted provider invoked; no agent financial posting.
Limitations: interrupted incomplete crews may repeat read-only inference; validated
result checkpoints avoid repeating completed reasoning. Detailed recovery documented.
Previous iteration eb0cbcf. Hash in final release manifest.

Verified implementation commit: `823ccff9d421bdf7431276b397c86abb4a64ff6f`.
