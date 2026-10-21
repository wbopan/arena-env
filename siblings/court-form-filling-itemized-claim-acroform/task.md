You are preparing a small-claims filing for a client. The inputs are in `/root/work`:

- `claim_form_blank.pdf`: a one-page fillable PDF (AcroForm) with text fields and checkboxes.
- `case.json`: the plaintiff, the defendant, the filing date (written out, e.g. "March 3, 2026"), and whether the plaintiff asked the defendant to pay before filing.
- `expenses.csv`: an itemized ledger with the columns `date` (MM/DD/YYYY), `description`, `amount` (USD) and `status` (`unpaid` or `paid`).

Fill the form and save it as `/root/work/claim_form_filled.pdf`. Set these fields:

- `plaintiff_name`, `plaintiff_address`, `defendant_name`, `defendant_address`: copy them exactly from `case.json`.
- `plaintiff_phone`: the 10-digit phone number formatted as `XXX-XXX-XXXX`.
- `claim_amount`: the sum of the `unpaid` rows only. Use two decimals, with no `$` sign and no thousands separators (e.g. `1834.20`).
- `period_start` and `period_end`: the earliest and latest dates among the `unpaid` rows, formatted `YYYY-MM-DD`.
- `filing_date`: the filing date from `case.json`, formatted `YYYY-MM-DD`.
- Checkbox `over_2500`: checked only if the claim amount is greater than 2500.00.
- Checkbox `asked_to_pay`: checked only if `case.json` says the plaintiff asked before filing.

To check a checkbox, set the field's value to its "on" export value. Leave unchecked boxes off.

The field `case_number` is for court use only. It must stay empty.
