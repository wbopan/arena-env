**Goal and output.** Open `nasa_budget_incomplete.xlsx`. Find every cell whose value is the string `"???"` on every sheet. Replace each one with a computed number (int or float, never a string). Save the result as `nasa_budget_recovered.xlsx` in the same directory as the input, unless the task location implies another directory. Keep everything else unchanged: sheet names, layout, headers and all other cells.

**Libraries.**
- Use openpyxl to read and write. `load_workbook(path)` keeps the structure.
- Write plain numeric values into the "???" cells, not Excel formulas. A grader reading with openpyxl or pandas sees formulas as strings, or as None/NaN when there is no cached value. The task explicitly asks for "the computed numeric value".
- The xlsx skill's "use formulas" rule does not apply here.
- If the input already contains formulas, check whether they have cached values with `load_workbook(p, data_only=True)`. Use the data_only copy for reading numbers. Save from the normal workbook, and only change the "???" cells.
- pandas `read_excel(sheet_name=None)` is fine for a quick look.

**Cheap inspection (do not print whole files).**
```python
from openpyxl import load_workbook
wb=load_workbook('nasa_budget_incomplete.xlsx')
for ws in wb:
    print(ws.title, ws.dimensions)
    for r in ws.iter_rows(min_row=1,max_row=3,values_only=True): print(r)
    print([c.coordinate for row in ws.iter_rows() for c in row if c.value=='???'])
```
Then print just the rows that contain "???", plus the header row, for each sheet.

**Typical sheet relationships to identify.** Expect sheets such as these:
- Budget by directorate × fiscal year, with a Total column and/or Total row.
- YoY % change.
- Percent share of total.
- Growth/CAGR summary.
- Possibly per-directorate or per-category detail.

Match rows and columns by label (directorate name, year), not by position. Sheets may order rows and columns differently.

**Formulas (from the data-reconciliation skill).**
- Sum constraint: `Missing = Total − Σ(known components)`. A missing Total is the sum of its components. This works across rows (directorates in a year) and columns (years).
- YoY forward: `Cur = Prev × (1 + YoY/100)`.
- YoY backward: `Prev = Cur / (1 + YoY/100)`.
- Missing YoY: `YoY = (Cur/Prev − 1) × 100`.
- Share: `Part = Total × Share/100`, so `Share = Part/Total × 100` and `Total = Part/(Share/100)`.
- CAGR over n = end_year − start_year periods (e.g. 5 years of data means n = 4): `CAGR = ((End/Start)^(1/n) − 1) × 100`. Rearranged: `End = Start × (1+CAGR/100)^n` and `Start = End/(1+CAGR/100)^n`.
- Check whether percentages are stored as 5.2 or as 0.052. Use the same convention as the neighbouring cells.

**Chain dependencies.** Some "???" cells can only be solved after others are filled. For example, a budget value is recovered from a row total, and a YoY or share cell in another sheet is then computed from it. Map the dependencies first, then resolve them in that order.

A simple robust approach is a fixed-point loop: repeatedly attempt every rule on every missing cell, fill the ones that become solvable, and stop when nothing changes. The simpler alternative is to hand-code each recovery explicitly after inspection, ordered by dependency.

Prefer primary data for derivations, i.e. raw budget values and sums. Use rounded percentages only when nothing else is available. Values back-computed from a rounded YoY or share are approximate.

**Rounding.** Match the precision used by the neighbouring cells in the same column or sheet.
- If the budgets there are whole numbers, round to int (or 1 decimal if that is what they use).
- If the percentages there have 1–2 decimals, round the same way.
- Compute from unrounded intermediate values, and round only when writing.

**Validation (do this before finishing).**
- Reload the output and assert that no cell anywhere equals "???".
- Assert that every filled cell is an int or float.
- Re-check the constraints:
  - Row sums equal the totals.
  - Column sums equal the totals.
  - Recomputed YoY matches the sheet within about 0.1.
  - Shares sum to about 100 and match Part/Total.
  - CAGR recomputes correctly.
- Print only the filled coordinates and values, plus any constraint mismatches.

**Step plan (about 10 commands).**
1. `ls`, then run the inspection one-liner to get sheet names, dimensions, headers and "???" coordinates.
2. Print the "???" rows with their labels, and the totals, for each sheet.
3. Decide which relationship solves each cell and the order to solve them in.
4. Write `recover.py`. It loads with openpyxl, builds label→cell maps for each sheet, computes the values in dependency order, writes the rounded numbers, and saves `nasa_budget_recovered.xlsx`.
5. Run it, then run a validation script for the constraints above and for "no ??? left / all numeric".
6. Fix any mismatches and re-run.
