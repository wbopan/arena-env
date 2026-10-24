## Reference notes

Use **pandas** for the CSV and the three Excel sheets; the deliverable is a CSV, so calculate in Python rather than writing Excel formulas.

```python
import pandas as pd
import numpy as np

prices = pd.read_csv('/root/work/gold_monthly.csv')
sheets = pd.read_excel('/root/work/reserves.xlsx', sheet_name=None)
# sheets['Value'], sheets['Volume'], sheets['Total Reserves']
```

- Check the imported column labels: Excel year headers may be integers (`2025`) or strings (`'2025'`). Select the matching label rather than assuming one type.
- Strip surrounding whitespace from `Country` **before** joining sheets. Keep the workbook’s spelling and capitalization. Empty Excel cells normally become `NaN`; use `pd.notna(...)`, not a truthiness check (zero is not missing).
- Match price periods by their `YYYYMmm` strings, not by row position alone. The Jan–Sep 2025 mean uses **nine prices**. The Jul, Aug, and Sep returns each need the preceding month’s price, including **June** for July.
- For prices \(P_t\), monthly return in percent is `100 * np.log(P_t / P_previous)`. For the three specified returns, use sample standard deviation: `returns.std(ddof=1)` (pandas `Series.std()` also defaults to `ddof=1`).
- Reserve value and volume units are already compatible: *millions of troy ounces × USD per troy ounce = USD millions*. Prefer a nonmissing 2025 `Value`; use `Volume × mean_price` only where that value is missing. Do not fill a missing total-reserves figure from another year.
- Compute exposure as `gold_value * sigma / 100` and RaR percentage as `exposure / total_reserves * 100`. A zero total-reserves denominator cannot yield a finite RaR; check for it before division.
- Sort using **unrounded** `rar_pct`, then export with the required column names and order. `df.to_csv('/root/work/rar.csv', index=False, float_format='%.4f')` writes numeric fields to four decimal places. Inspect the header and a few output rows after writing.
