**Goal and output.** Edit `gdp.xlsx` in place. Load it with openpyxl without `data_only`, write formulas into the existing "Task" sheet only, and save to the same path `gdp.xlsx`. Do not add sheets, macros or styling. Do not touch fills, fonts or number formats: assigning `cell.value` alone keeps the style. Every result cell must contain an Excel formula, never a hardcoded Python value. The file must recalculate with zero errors (#N/A, #REF!, #DIV/0!, #NAME?, #VALUE!).

**Step 1: Inspect cheaply (2–4 commands).** Dump only the non-empty cells you need. Keep `repr` so you can see value types.
```python
from openpyxl import load_workbook
wb=load_workbook('gdp.xlsx'); t=wb['Task']; d=wb['Data']
for r in range(1,60):
    row=[(c.coordinate,repr(c.value)) for c in t[r][:14] if c.value is not None]
    if row: print(row)
```
Do the same for Data rows 1–45, but only for the first ~25 columns, truncating long strings.

Find and note:
- **Task sheet:**
  - The series codes in column D for rows 12–17, 19–24 and 26–31.
  - The years in H10:L10, and whether they are int, float or text.
  - The block labels in columns B/C/E. Which block is exports, which is imports, which is GDP?
  - The country names.
  - The labels of the statistics rows below row 40: min, max, median, mean, P25, P75, weighted mean. Note their exact cells and which columns (H:L) they span.
  - Any unit or label hints, such as "in percent" or a weighting row.
- **Data sheet, rows 21–40:**
  - Which column holds the series code.
  - Which row holds the year headers, and their type. If years are text in one sheet and numbers in the other, MATCH fails with #N/A.
  - The first and last data columns.
  - Whether codes are unique.
  - Units: are exports, imports and GDP in the same currency and scale?
- **Formatting of H35:L40:** check `t['H35'].number_format`. If it is a `%` format, compute a plain ratio. If it is a plain number format (e.g. `0.0`) under a "percent of GDP" label, multiply by 100.

**Step 2: Lookup formulas (H12:L17, H19:L24, H26:L31).** Use INDEX/MATCH with two conditions: the row is matched on the code and the column on the year. Prefer INDEX/MATCH over XLOOKUP, because LibreOffice recalculation may not support XLOOKUP and openpyxl needs `_xlfn.` prefixes for it. Template, with Data codes assumed in column X, years in header row Y, and data columns A..Z adjusted after inspection:
```
=INDEX(Data!$A$21:$Z$40, MATCH($D12, Data!$X$21:$X$40, 0), MATCH(H$10, Data!$A$Y:$Z$Y, 0))
```
The column range inside INDEX and in the year MATCH must start at the same column. Use mixed refs (`$D12`, `H$10`) so one pattern fills the whole block. Generate the formulas in a loop over rows and columns using `openpyxl.utils.get_column_letter`.

If a year type mismatch exists, use one of these inside the MATCH:
- `MATCH(VALUE(H$10),…)` when the Task year is text and the Data years are numbers.
- `MATCH(TEXT(H$10,"0"),…)` when the Task year is a number and the Data years are text.

**Step 3: Net exports in % of GDP (H35:L40).** For each country i (0–5), use the same row offset in each block:
```
=(H{12+i}-H{19+i})/H{26+i}*100    (drop *100 if cell format is %)
```
Verify against the labels which block is exports, which is imports and which is GDP. Countries must align row-by-row across the blocks; check the country names.

**Step 4: Statistics, for each year column H:L, over rows 35:40.** Use these formulas:
- `=MIN(H35:H40)`
- `=MAX(H35:H40)`
- `=MEDIAN(H35:H40)`
- `=AVERAGE(H35:H40)`
- `=PERCENTILE(H35:H40,0.25)`
- `=PERCENTILE(H35:H40,0.75)`

QUARTILE(...,1) and QUARTILE(...,3) give the same inclusive result. Avoid the `.INC` variants unless you write `_xlfn.PERCENTILE.INC`. Put each formula into the row whose label matches it; do not assume the order.

**Step 5: Weighted mean with SUMPRODUCT.** GCC aggregate net exports/GDP is weighted by each country's GDP:
```
=SUMPRODUCT(H35:H40,H26:H31)/SUM(H26:H31)
```
This equals (ΣX−ΣM)/ΣGDP (×100). Use it only if all GDP values are in the same currency and scale; check the units in the Data sheet. If the template has an explicit weights row or column, use that instead.

**Step 6: Save, recalc, verify.**
```bash
python recalc.py gdp.xlsx 60
```
The status must be `success` with `total_errors` equal to 0. Locate `recalc.py` with `ls` or `find / -name recalc.py 2>/dev/null | head -1` if it is not in the current directory.

Then spot-check values with `load_workbook('gdp.xlsx',data_only=True)`. Print H12, H19 and H26, plus the stats and weighted mean for one or two columns, and compare them with the raw Data cells. Also sanity-check that min ≤ P25 ≤ median ≤ P75 ≤ max, and that the weighted mean lies within [min, max].

Never save a workbook that was opened with `data_only=True`, because that permanently replaces the formulas.

**Pitfalls:**
- Off-by-one block rows: 12–17, 19–24 and 26–31 each hold 6 countries, and 35–40 holds the 6 results.
- Wrong INDEX column origin.
- Exact match needs the `0` argument in MATCH.
- Codes with trailing spaces: if MATCH returns #N/A, check `repr` and use `TRIM` if needed.
- Do not write outside the yellow and statistics cells.
- Keep existing formatting untouched.
