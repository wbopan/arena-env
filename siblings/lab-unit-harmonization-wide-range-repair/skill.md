## Reference notes

Use Python’s standard-library `csv` module so quoted decimal-comma cells (for example, `"12,34"`) are read as one field. Open CSV files with `newline=''`; `csv.DictReader` preserves header order, and `csv.DictWriter(..., fieldnames=header)` writes that order. Read `patient_id` as text and never reformat it.

```python
import csv

with open('/root/work/labs_wide.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    header = reader.fieldnames
    lab_cols = header[1:]
    # Process rows in reader order.
```

Use **`lab_reference.csv` as the authority** for each feature’s inclusive `min`/`max` and its ordered `alt_factors`; do not substitute factors from a clinical reference table. Split nonempty `alt_factors` on `;` and retain their order. `unit` describes the target unit; it is not an additional conversion instruction.

For each row, first check *all* lab cells for missingness: `cell.strip()` is empty, `NA`, or `NaN` (a case-insensitive comparison is convenient). Drop the entire row if any lab is missing. For surviving rows, strip whitespace and replace `,` with `.` before numeric parsing. Commas are **never** thousands separators; scientific notation can then be parsed normally.

For each parsed value `x` and its reference entry:

```python
if minimum <= x <= maximum:
    chosen = x
else:
    chosen = x
    for factor in factors:             # reference-file order
        candidate = x * factor
        if minimum <= candidate <= maximum:
            chosen = candidate
            break
```

Do not clamp, add a range tolerance, or try further factors after the first in-range product. Format the chosen number with `f"{chosen:.2f}"` for exactly two decimal places, without grouping or scientific notation. Write only surviving rows, in input order, to `/root/work/harmonized.csv` with the original header.
