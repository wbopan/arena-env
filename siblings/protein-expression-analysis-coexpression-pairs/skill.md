## Reference notes

Use **openpyxl** to read both named sheets while retaining the workbook’s ID cell values, and Python’s **json** module for the output. No Excel formulas or workbook edits are needed.

```python
from openpyxl import load_workbook

wb = load_workbook("/root/work/coexpression_panel.xlsx", read_only=True, data_only=True)
data_rows = wb["Data"].iter_rows(values_only=True)
data_headers = next(data_rows)
pair_rows = wb["Pairs"].iter_rows(values_only=True)
pair_headers = next(pair_rows)
```

Build column-index maps from each header row rather than assuming column positions. Use the six sample headers from `Data` in a consistent order for *both* proteins; map `Protein_ID` to its measurement row. Look up `Pair_ID`, `Protein_A`, and `Protein_B` by their headers, preserving A/B and the ID values from each pair row.

Pearson correlation for vectors \(x,y\) of the six matched log2 measurements is
\[
r=\frac{\sum_i(x_i-\bar x)(y_i-\bar y)}
        {\sqrt{\sum_i(x_i-\bar x)^2\sum_i(y_i-\bar y)^2}}.
\]
Alternatively, `float(numpy.corrcoef(x, y)[0, 1])` computes it. Keep the **unrounded** result for sorting by `(-abs(r), pair_id)`; apply `round(r, 4)` only to the JSON `pearson_r` value.

Write with `json.dump(...)`. The top-level value should be an object, `pairs` an array, and each `pearson_r` a JSON number—not a formatted string. After writing, reopen the JSON to check its keys, entry count, and first entry’s ID against `strongest_pair_id`.
