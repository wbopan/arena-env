## Reference notes

- Use `openpyxl` to read the `Results` sheet and the standard-library `csv` module to write the CSV. This output does **not** require Excel formulas or workbook changes.
- `load_workbook(path, read_only=True, data_only=True)` reads cached values from formula cells; `iter_rows(values_only=True)` yields tuples. Map columns by header name rather than assuming fixed positions.

```python
from openpyxl import load_workbook
import csv
import math

wb = load_workbook("/root/work/meet.xlsx", read_only=True, data_only=True)
rows = wb["Results"].iter_rows(values_only=True)
headers = next(rows)
for values in rows:
    record = dict(zip(headers, values))
    # calculate and collect an output row
```

- Empty spreadsheet cells read as `None`. Check each required lift **before** summing: an empty or nonpositive lift invalidates an SBD total; only the bench matters for B. Do not treat a missing lift as zero while summing otherwise valid lifts.
- Select parameters using the task’s table: `Mx → M`; `Raw` and `Wraps → Raw`; `Single-ply` and `Multi-ply → Equipped`. Do not use DOTS or Wilks coefficients.
- For bodyweight below 35 kg or a zero total, points are zero. Otherwise, with the selected `(A, B, C)`, use `denominator = A - B * math.exp(-C * bodyweight)` and `points = total * max(0.0, 100.0 / denominator)`. Guard against a zero denominator before division, as in the Good Lift implementation.
- Keep numeric values for sorting. Round/format output to one decimal for `TotalKg` and two for `GLPoints`; sort by descending output points, then ascending `Name`. `csv.writer` handles quoting names containing commas. Write the four headers in the requested order, with no extra index column.

Workflow: inspect only the sheet headers and a few rows, write one short Python script, run it, then inspect the CSV header, row count, formatting, and ordering.
