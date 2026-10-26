## Reference notes

Use **pandas** to read the named Excel sheets and Python’s **csv** and **statistics** modules for the output and calculations. This task produces a CSV, so Excel formulas and recalculation are unnecessary.

```python
import pandas as pd

path = "/root/work/paired_expression.xlsx"
data = pd.read_excel(path, sheet_name="Data", dtype={"Protein_ID": str})
pairs = pd.read_excel(path, sheet_name="Pairs", dtype=str)
targets = pd.read_excel(path, sheet_name="Targets", dtype={"Protein_ID": str})
```

- Read headers to locate sample columns by their **full names**; do not rely on column positions. Match `Protein_ID` values exactly and iterate over `targets["Protein_ID"]` to preserve target order. Keep repeated listed pairs if any.
- For each pair, `delta = treated_log2_value - control_log2_value`. The mean is `sum(deltas) / len(deltas)`; the sample standard deviation uses denominator `n - 1` (`statistics.stdev(deltas)` for at least two values). Geometric fold change is `2 ** mean`, calculated **before** rounding the mean.
- Write with `csv.writer` and `open(output_path, "w", newline="")` for ordinary CSV quoting and line endings. Format each reported floating-point result with `f"{value:.4f}"`; write `n_pairs` as a count. Use precisely the requested header and no index column.
- Before finishing, inspect the CSV header and a few rows, and confirm the number and order of output rows match `Targets`.
