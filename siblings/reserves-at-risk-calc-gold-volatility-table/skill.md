## Reference notes

Use **openpyxl** for the workbooks and Python’s `math` and `statistics` modules for the calculations. The task explicitly requires **literal values**, so calculate in Python; do not write Excel formulas or run formula recalculation.

```python
from openpyxl import load_workbook, Workbook
import math, statistics

src = load_workbook("/root/work/gold_prices.xlsx", read_only=True, data_only=True)
ws = src["Prices"]
months = ws.iter_rows(min_row=4, min_col=1, max_col=2, values_only=True)
```

`iter_rows(..., values_only=True)` yields `(Period, Gold)` values in worksheet order. Rows 1–2 are notes; row 3 is the header. Keep IMF-style periods such as `2022M01` as strings rather than parsing them as dates.

- Monthly return, **in percent**: `100 * math.log(current_price / previous_price)`.
- For a window of exactly 3 or 12 available returns ending at the current month, use `statistics.stdev(window)`; it uses the required **sample** standard deviation (`n−1`). Do not include the first month’s missing return in a window.
- Annualized 3-month volatility: `vol3 * math.sqrt(12)`. These volatility columns retain the same percent units as `LogReturn`.
- Apply `round(value, 6)` to each computed value. Use `None` for unavailable results so the Excel cells remain empty.

For the new file, `Workbook()` creates a sheet accessible as `out.active`; set its `title` to `Volatility`, use `out.append([...])` for the exact six-column header and subsequent rows, then `out_wb.save("/root/work/gold_vol.xlsx")`. Openpyxl rows and columns are 1-based.

**Short workflow:** inspect the source header and a few data rows; read the two source columns once; maintain returns in chronological order while building output rows; save; reopen the output to check its sheet name, header, row count, early blanks, and that computed cells are numeric rather than formulas.
