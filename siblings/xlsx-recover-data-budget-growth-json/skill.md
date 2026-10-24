## Reference notes

Use **openpyxl** to read the workbook and Python’s **json** module to write the result. The deliverable is JSON, not a modified spreadsheet; no formula recalculation is needed.

```python
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
import json

wb = load_workbook('/root/work/budget_incomplete.xlsx')
missing = {
    f'{ws.title}!{cell.coordinate}'
    for ws in wb
    for row in ws
    for cell in row
    if cell.value == '???'
}
# Inspect only the small tables, e.g. each sheet's rows 1–6.
# Keep `missing` unchanged while recovering values.
```

Cell indices are **1-based**. For each department row, `Budget` columns **B–G** correspond to FY2019–FY2024; `YoY (%)` columns **B–F** correspond to FY2020–FY2024. Thus a YoY value in column B relates Budget **C to B**, and one in column F relates Budget **G to F**. `Summary!B` relates Budget G to B; `Summary!C` uses all six Budget values.

All percentage figures are in **percent units**, not fractions:

- `current = previous * (1 + yoy / 100)`
- `previous = current / (1 + yoy / 100)`
- `yoy = (current / previous - 1) * 100`
- `end = start * (1 + cagr / 100) ** 5`
- `start = end / (1 + cagr / 100) ** 5`
- `cagr = ((end / start) ** (1 / 5) - 1) * 100`
- `average = sum(six_budgets) / 6`; if only one budget is unknown, estimate it with `6 * average - sum(known_budgets)`.

**Rounding matters:** source budgets are integers, while provided YoY/CAGR values were rounded to **4 decimals** and averages to **2 decimals**. Inverting a displayed rate or average may yield a non-integer approximation: select an integer budget consistent with the rounded relationships rather than treating the displayed figure as exact. Recover dependent budget cells first, then calculate missing percentages and averages from those budgets. Revisit rows until no further cells can be resolved.

For each originally marked cell only, emit a JSON **number**: nearest integer for Budget; `round(value, 2)` for YoY, CAGR, and average. Do not output filled-in values for cells that were not originally `???`.

```python
with open('/root/work/recovered.json', 'w') as f:
    json.dump(results, f)
```

Before writing, check that `set(results) == missing` and that the recovered budgets reproduce the supplied rates and averages at their respective displayed precisions.
