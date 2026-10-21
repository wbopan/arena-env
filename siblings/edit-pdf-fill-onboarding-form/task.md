An HR onboarding form must be filled in from an update note.

Inputs:
- `/root/work/onboarding_form.pdf`: a one-page PDF with interactive (AcroForm) text fields named `full_name`, `employee_id`, `department`, `start_date`, `annual_salary` and `monthly_salary`. Some fields may already contain stale values.
- `/root/work/update.txt`: bullet lines of the form `- Key: value`. This file is the source of truth.

Fill every one of the six fields, overwriting anything already there. Save the result as `/root/work/onboarding_filled.pdf`.

The output must remain a one-page PDF that still contains those same six form fields, with their values stored in the fields. Do not flatten or rasterize the page. The printed title and labels must remain.

Field values:
- `full_name`: the legal name, exactly as written. Never use the nickname or preferred name.
- `employee_id`: the employee number, exactly as written.
- `department`: the current team, not any previous team.
- `start_date`: the first day, formatted `MM/DD/YYYY` with zero padding.
- `annual_salary`: the yearly base pay as a plain number with exactly two decimals. Use no currency symbol and no thousands separators (for example `84500.00`).
- `monthly_salary`: the annual base pay divided by 12, rounded half-up to two decimals, in the same plain format.

Ignore any other keys in the update note.
