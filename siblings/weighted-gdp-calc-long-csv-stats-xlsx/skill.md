## Reference notes

Use **pandas** to read and reshape the CSV, **NumPy** for inclusive percentiles, and **openpyxl** to write numeric Excel cells. The task explicitly requires hardcoded numeric results—not formulas—and integer year headers.

```python
import pandas as pd
import numpy as np
from openpyxl import Workbook, load_workbook

df = pd.read_csv('/root/work/trade_long.csv')
print(df.shape, df.columns.tolist())
print(df['unit'].value_counts(dropna=False))
```

- Normalize **each row before pivoting**: `USD bn` values can remain unchanged; divide `USD mn` values by `1000` to express them in `USD bn`. Check for unexpected units and missing values.
- Check that each `(country, year, indicator)` occurs once. Then reshape with `df.pivot(index=['country', 'year'], columns='indicator', values='value_bn')`. Confirm each country-year has GDP, exports and imports, and GDP is nonzero.
- Compute `nx_pct = (exports_gs - imports_gs) / gdp_current * 100`. These values are already in *percentage points*: an NX% of 12.345 is stored as the number `12.345`, **not** `0.12345` with Excel’s `%` number format.
- For each year, calculate statistics across its six country rows. `np.percentile(values, [25, 75], method='linear')` uses the inclusive, linearly interpolated definition: for sorted values of length `n`, the zero-based rank is `(n - 1) * p`. Use the simple unweighted mean for `Mean`.
- Compute `Weighted Mean` as `sum(nx_pct * gdp_current) / sum(gdp_current)` **within that year**. Equivalently, `sum(exports_gs - imports_gs) / sum(gdp_current) * 100`, provided all three indicators use the same normalized unit.

For exact cell placement, create a workbook with `wb = Workbook()`, set `ws = wb.active` and `ws.title = 'Stats'`, then assign cells with `ws.cell(row=..., column=..., value=...)` (indices are 1-based). Sort years and write `int(year)` in row 1; write statistics in the specified row order. Store each result as `round(float(result), 3)` and optionally set its Excel `number_format = '0.000'`—**not** a percent format. Save with `wb.save('/root/work/nx_stats.xlsx')`.

After saving, reopen with `load_workbook(path, data_only=True)` and spot-check sheet name, headers, dimensions, numeric cell types and a few values against the normalized data.
