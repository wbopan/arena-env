## Reference notes

Use `openpyxl` to read the three sheets and create a new `.xlsx` file. This task explicitly requires **numeric values, not formulas**, so calculate in Python; do not write Excel formulas or run formula recalculation.

```python
from openpyxl import load_workbook, Workbook
from math import exp

src = load_workbook('/root/work/shock_inputs.xlsx', data_only=True)
baseline = list(src['Baseline'].values)   # first tuple is the header
investment = list(src['Investment'].values)
params = list(src['Params'].values)

out = Workbook()
ws = out.active
ws.title = 'Shock'
ws.append(['year', 'I', 'dK', 'K_with',
           'Ystar_base', 'Ystar_with', 'gap_pct'])
# ws.append([...]) writes one result row.
out.save('/root/work/shock_results.xlsx')
```

Build lookups using the **header names**, rather than assuming column positions. Map investment by year; missing years have `I = 0`, and investment rows are unsorted. Read `alpha` and `delta` by parameter name. Process baseline rows in ascending numeric year order, carrying `dK` forward from an initial zero. For each year, apply same-year investment **before** computing `K_with` and output:

- `dK = (1 - delta) * previous_dK + I`
- `K_with = K_base + dK`
- `Ystar_base = exp(lnZ_trend) * K_base ** alpha`
- `Ystar_with = exp(lnZ_trend) * K_with ** alpha`
- `gap_pct = 100 * (Ystar_with / Ystar_base - 1)`

Keep `year` and all result cells numeric. Python floats retain sufficient precision without rounding; if rounding, use six decimal places. After saving, reopen the output with `data_only=True` and inspect its sheet name, header, row count, and a few numeric cells.
