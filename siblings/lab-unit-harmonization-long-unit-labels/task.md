# Convert a long-format lab export by unit label and summarize

`/root/work/measurements.csv` is a long-format lab export with columns `patient_id,analyte,value,unit`. It was merged from several sites. The sites report in different units and spell unit labels inconsistently.

Normalize each unit label as follows:
1. Trim whitespace.
2. Lower-case the label.
3. Treat `µ` (U+00B5) and `μ` (U+03BC) as `u`.

Values may use a comma as the decimal separator (`5,4` = 5.4).

Convert every value to US conventional units by multiplying by the factor for its normalized unit:

| analyte | target unit | normalized unit: factor |
|---|---|---|
| Creatinine | mg/dL | mg/dl: 1; umol/l: 1/88.4 |
| BUN | mg/dL | mg/dl: 1; mmol/l: 2.8 |
| Hemoglobin | g/dL | g/dl: 1; g/l: 0.1; mmol/l: 1.611 |
| Calcium | mg/dL | mg/dl: 1; mmol/l: 4.0; meq/l: 2.0 |
| Glucose | mg/dL | mg/dl: 1; mmol/l: 18.016 |
| Albumin | g/dL | g/dl: 1; g/l: 0.1 |

Drop a row if any of these is true:
- Its value is empty or not a finite number (e.g. `NA`).
- Its normalized unit is not listed for that analyte.

Write `/root/work/lab_summary.json` with this structure:

```
{"dropped_rows": <int>,
 "analytes": {"<analyte>": {"n": <int>, "mean": <float>, "min": <float>, "max": <float>}, ...}}
```

Requirements:
- Include one entry for each of the six analytes. Use the exact names from the table.
- Compute the statistics on the converted values of the kept rows.
- Round `mean`, `min` and `max` to 2 decimals.
