**Goal and output.** Edit `/root/data/openipf.xlsx` in place. Leave sheet "Data" untouched. Fill the existing empty sheet "Dots" as follows:
- Row 1 holds headers. Rows 2 and down hold one row per Data row, in the same order.
- Columns: first the needed columns copied from Data, then `TotalKg` (an Excel formula), then `Dots` (an Excel formula).
- Copied columns keep the exact header names and the relative left-to-right order they have in Data. Include the lifter's name column.
- Both new columns must be real formulas (strings starting with `=`), not values computed in Python.
- Keep 3-decimal precision by wrapping the formulas in `ROUND(...,3)`.

**Which columns are needed.** Dots needs four things:
- Sex, to choose the men's or women's coefficients.
- Bodyweight in kg.
- Total in kg, which is the sum of the best squat, best bench and best deadlift.
- The lifter's name, which is also required.

In the OpenPowerlifting/OpenIPF schema these are typically `Name`, `Sex`, `BodyweightKg`, `Best3SquatKg`, `Best3BenchKg` and `Best3DeadliftKg`. Do not copy Data's own `TotalKg`, since you must compute it. Confirm the names and order by reading `/root/data/data-readme.md` (grep it) and the Data header row.
- In OpenPowerlifting, negative lift values mean a failed attempt. A blank Best3 means no successful lift.
- Check Sex values: M, F, possibly Mx. Mx uses the men's coefficients.

**Dots formula (OpenPowerlifting implementation).** In the skill's Rust code, `poly4(A,B,C,D,E,x)` means A·x⁴ + B·x³ + C·x² + D·x + E. The coefficient is then:

coef = 500 / (A·bw⁴ + B·bw³ + C·bw² + D·bw + E)

| | Men (M, Mx) | Women (F) |
|---|---|---|
| A | -0.0000010930 | -0.0000010706 |
| B | 0.0007391293 | 0.0005158568 |
| C | -0.1918759221 | -0.1126655495 |
| D | 24.0900756 | 13.6175032 |
| E | -307.75076 | -57.96288 |
| Bodyweight clamp | 40 to 210 | 40 to 150 |

- Dots = coef × TotalKg.
- If bodyweight or total is 0, Dots = 0.
- Clamp bodyweight in Excel with `MIN(MAX(bw,40),210)`.

**Excel formula templates.** These assume a column layout of A=Name, B=Sex, C=BodyweightKg, D/E/F = squat/bench/deadlift, G=TotalKg and H=Dots. Adjust the letters to the actual layout.
```
G{r}: =ROUND(SUM(D{r}:F{r}),3)
H{r}: =IF(OR(C{r}=0,G{r}=0),0,ROUND(G{r}*500/IF(B{r}="F",
   -0.0000010706*MIN(MAX(C{r},40),150)^4+0.0005158568*MIN(MAX(C{r},40),150)^3-0.1126655495*MIN(MAX(C{r},40),150)^2+13.6175032*MIN(MAX(C{r},40),150)-57.96288,
   -0.000001093*MIN(MAX(C{r},40),210)^4+0.0007391293*MIN(MAX(C{r},40),210)^3-0.1918759221*MIN(MAX(C{r},40),210)^2+24.0900756*MIN(MAX(C{r},40),210)-307.75076),3))
```
Write the H formula on one line in code.
- SUM treats blanks as 0.
- If the data contains negative (failed) best lifts, decide whether to sum them. Only change the approach if the readme says Data's TotalKg excludes them. You can compare against Data's own TotalKg column for a sanity check.

**Tools.**
- Use openpyxl, not pandas, so that formulas are written and the Data sheet keeps its formatting:
  ```python
  from openpyxl import load_workbook
  wb = load_workbook(p)
  d, s = wb['Data'], wb['Dots']
  ```
- Do not use `data_only=True` when you save.
- Read Data's headers with `[c.value for c in d[1]]`, map each name to its column index, then copy values row by row (`d.cell(r, ci).value`).
- Write the formulas into `s.cell(r, col)` and call `wb.save(p)`.
- Recalculate with LibreOffice through the skill's `recalc.py`. Find it with `find / -name recalc.py 2>/dev/null | head`, then run `python recalc.py /root/data/openipf.xlsx 60`.
- Check that the returned JSON has `"status": "success"` and 0 errors.
- If recalc.py is absent, use `soffice --headless --convert-to xlsx` into a temporary directory to verify values only. Keep the original file with its formulas.

**Pitfalls.**
- Excel rows are 1-based and the header is row 1, so the first data row is row 2.
- Sex strings may contain whitespace, so check `set()` of the Sex values.
- Do not hardcode computed numbers; the grader likely checks that the cells are formulas and also checks their values.
- Make sure the Dots sheet has no leftover cells.
- Do not print whole files; use `head` or small slices.

**Steps.**
1. Run `grep -n -i -E "name|sex|bodyweight|best3|total" /root/data/data-readme.md | head -40`.
2. Write a python one-liner that loads the workbook and prints the sheetnames, `d.max_row`, `d.max_column`, the Data header row, 3 sample rows and `set` of the Sex values. Also count blank and negative values in the lift columns.
3. Write `/root/sol.py` that copies the selected columns in Data order (headers and values), then adds the `TotalKg` and `Dots` headers and the formulas for every row. Save in place.
4. Run it, then run recalc.py and confirm 0 errors.
5. Verify with `load_workbook(p, data_only=True)['Dots']`:
   - Print the header row and the first 3 rows.
   - Recompute Dots in Python for a few rows and compare to 3 decimals.
   - Check that row counts match Data.
   - Check with a non-data_only load that the cells still hold formulas.
