## Reference notes

Use **openpyxl** to edit the existing workbook in place; this preserves its sheet, layout, and cell formatting. This task explicitly requires recovered values to be **numeric constants, not formulas**.

```python
from openpyxl import load_workbook

wb = load_workbook('/root/work/sales_incomplete.xlsx')
ws = wb['Quarterly Sales']
missing = [(r, c) for r in range(2, 11) for c in range(2, 7)
           if ws.cell(r, c).value == '???']
# Assign a recovered integer with ws.cell(r, c).value = int(value).
wb.save('/root/work/sales_recovered.xlsx')
```

`openpyxl` row and column indices are **1-based**: B–F are columns 2–6. Only assign to cells recorded in `missing`; leave every other value untouched. Do not load with `data_only=True` when editing, since that can discard formulas in an existing workbook.

For reconciliation, express each row as `B + C + D + E − F = 0` (rows 2–10), and each column as `sum(rows 2–9) − row 10 = 0` (columns B–F). An equation with exactly one unresolved cell gives that cell directly; repeat passes because resolving one cell can unlock another. If passes stall, form a linear system over the remaining unknown cells using these same equations and solve it with `numpy.linalg.lstsq(A, b, rcond=None)` or `numpy.linalg.solve(A, b)` if square. Check the solution is uniquely determined, integral, and satisfies **every equation exactly** before writing integers.

Run one short script, then reopen the saved file and check that no `???` remains, recovered cells have integer numeric values, and all row and column sums match.
