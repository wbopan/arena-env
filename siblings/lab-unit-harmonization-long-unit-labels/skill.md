## Reference notes

Use Python’s standard-library `csv`, `math`, and `json`; no clinical-range lookup is needed. The task’s unit labels and factors are authoritative: **convert by normalized unit label, not by the value’s apparent range**. Do not clamp values or round individual converted measurements.

```python
import csv, json, math

with open("/root/work/measurements.csv", newline="", encoding="utf-8-sig") as f:
    rows = csv.DictReader(f)
    for row in rows:
        analyte = row["analyte"]  # preserve the task's exact analyte names
        unit = row["unit"].strip().lower().replace("µ", "u").replace("μ", "u")
        try:
            value = float(row["value"].strip().replace(",", "."))
        except ValueError:
            # drop this row
            continue
        if not math.isfinite(value):
            # drop this row
            continue
        # Look up (analyte, unit) in the task's factor table;
        # if absent, drop the row. Otherwise retain value * factor.
```

An empty value fails `float()`; strings such as `NA` also fail, while `nan` and `inf` require the explicit `math.isfinite()` check. CSV fields containing decimal commas must be quoted in the input to remain one field; `csv.DictReader` handles CSV quoting.

Initialize collections for **all six** analytes so each appears in the JSON. Count every dropped input row once, even if it has multiple problems. Compute count, mean, minimum, and maximum from the *unrounded converted values*, then round the three statistics to two decimal places. Write numeric JSON values, not formatted strings:

```python
with open("/root/work/lab_summary.json", "w", encoding="utf-8") as f:
    json.dump(result, f, allow_nan=False)
```

A short workflow: inspect the CSV header and a few rows cheaply; write one script with the task’s factor table; run it; inspect the JSON structure, counts, and representative conversions.
