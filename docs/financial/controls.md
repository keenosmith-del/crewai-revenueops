# Financial controls
Numeric(20,3) stores amounts; Decimal validates the explicitly supported ISO currency
subset ZAR/USD/EUR/GBP (2 places), JPY (0), KWD (3). Unsupported precision, NaN,
infinity, floats and amounts >= 10^12 are rejected. No FX or rounding occurs.
Outstanding = invoice original amount − immutable allocations. Available receipt =
transaction amount − immutable allocations. Reversals are review-only, never treated
as positive receipts. Gross received includes suspected duplicates, which remain
unallocated and blocked. Totals are per currency; no consolidated mixed-currency KPI.

Matching: bounded reference tokens, currency, customer, outstanding amount. Exact,
partial, overpayment and explicit combined reference matches are proposals. A unique
customer/amount match is lower confidence. Bounded 2–3 invoice combinations are
candidates, never automatic allocations. Unknown customer blocks approval until a reviewer records a verified customer account
through the audited transaction verification API. Allocated receipts cannot be reassigned.

Imports validate the whole file before confirmation. SHA-256 plus mapping and unique
source identifiers prevent reimport effects. Separate transactions with the same
reference/amount/date/account are flagged as possible duplicates. Review is conservative.
No adjustment, refund execution, credit note, general ledger posting or tax engine exists.

Approval serialises organisation writes, locks case then transaction and sorted invoice
rows, revalidates balances/currency/customer/disputes and writes allocations, review,
audit and idempotency result in one transaction. Rejects never write allocations.
Ordinary application users cannot modify immutable financial history through an API.
