# Synthetic CSV templates
These one-row fictional examples extend the seeded SYN-000 account. Import invoices
first, then transactions, preview/confirm both and run reconciliation. The exact 17.35
ZAR proposal requires reviewer approval. Re-uploading identical files is idempotent.
Use decimal text, ISO dates and the documented currency subset. Customers must already
exist; create/verify customer accounts through authorised forms. To map other headers,
enter e.g. {"reference":"Invoice number","amount":"Gross"} in the import form.
The full synthetic dataset is in data/synthetic; importing it into an already seeded
workspace correctly reports duplicate identifiers. Never portray these files as bank data.
