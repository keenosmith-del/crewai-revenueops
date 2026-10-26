# Reproducible synthetic demonstration
1. Start Compose as documented; seed once. Sign in as reviewer@revenueops.example with
   Demo-finance-2026!. Confirm the Synthetic demonstration label.
2. Inspect overview, currency/date filters, aged balances and activity. These are actual
   database queries over fictional records, not static counters.
3. Open Invoices → Import invoices. Choose data/templates/invoices.csv. Inspect the one-row
   preview, then confirm. Repeat for data/templates/transactions.csv under Transactions.
   Importing the full data/synthetic files into an already seeded workspace should report
   duplicates; this is expected duplicate protection, not an error to bypass.
4. Run reconciliation. Search the imported payment source ID under Transactions and inspect
   its generated transaction ID. In Reconciliation search that ID and open the exact proposal.
5. Inspect invoice/amount fields and supporting evidence. In baseline mode a CrewAI request
   records not_executed. Never portray that state as agent inference.
6. Enter a meaningful review note and approve the supported 17.35 ZAR allocation. Invoice
   detail now shows zero outstanding; transaction shows zero unallocated. Reload and verify
   the persisted state and review audit. No float balance was supplied by the browser.
7. For genuine local inference, configure MODEL_MODE=ollama and the appropriate OLLAMA_URL,
   then recreate API/worker. Keep the installed local llama3.2:3b model; no hosted key needed.
8. Create customer Synthetic Model Probe, account SYN-PROBE, email probe@customer.example.
   Import local-model-invoices.csv and local-model-transactions.csv. Run reconciliation;
   the 25.00 receipt without an invoice reference becomes an exception against a small
   one-invoice account. This keeps the local-model context manageable.
9. Open that investigation and request CrewAI. Refresh Agent workspace to inspect actual
   mode/model, stage, tool calls, task audit, structured result, validation and usage. These
   fields are populated only by execution. Do not imply agent work succeeded if the job fails.
10. Inspect the investigator/quality result and exact cited fields. Reviewers may reject,
    request information or authorise only independently supported allocations. An agent's
    recommendation alone is not permission to post. The supplied small case is intentionally
    suited to requesting clarification, rather than inventing a reference.
11. Inspect updated balances and account history. Under Collections select an undisputed
    overdue invoice, prepare a template draft, review and approve it. The state becomes
    approved_not_sent; no sender or external communication exists.
12. Inspect Audit, Reports CSV export and evaluation evidence. Explain the 13-case baseline,
    separate mocked contracts, actual small-model success and 3-case comparison. Disclose
    that larger attempts timed out or failed validation without changing financial balances.
13. Show verify.yml and deploy-staging.yml, exact local results and release manifest. The
    GitHub badge points at the prepared workflow; hosted CI is unverified until an authorised
    push produces a run. Staging requires external configuration and independent approval;
    nothing has been provisioned or deployed.

Automated demonstration: five Playwright cases against a separate disposable PostgreSQL
fixture cover both imports, explicit baseline disclosure, approval/persisted balances,
unsent collection drafts, audit, all pages and responsive navigation. They deliberately
refuse the main demo or any non-test environment. See deployment/local.md for isolation.
