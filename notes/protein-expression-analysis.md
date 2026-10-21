**Goal recap (format only).** Edit `protein_expression.xlsx` in place, on the sheet "Task", using live Excel formulas only. Do not hard-code numbers, add macros, or change formats, colors or fonts. Keep the same filename and .xlsx format. There must be zero formula errors (#N/A, #REF!, #DIV/0!, #NAME?, #VALUE!).

- C11:L20 is a two-way lookup from sheet "Data". Rows are the protein IDs in Task!A11:A20. Columns are the sample names in Task!C10:L10.
- Rows 24–27, columns B–K (yellow) hold control mean, control SD, treated mean and treated SD.
- Rows 32–41 hold one row per protein. Column C is Log2FC = TreatedMean − ControlMean. Column D is FC = 2^Log2FC.

**Tools.**
- Use openpyxl `load_workbook(path)` to edit. Never pass `data_only=True` when saving, because that destroys formulas.
- pandas or openpyxl `read_only` is fine for quick inspection.
- After saving, run `python recalc.py protein_expression.xlsx 60`. It recalculates in LibreOffice and returns JSON with `status`, `total_errors` and `error_summary`.
- Verify values afterwards with `load_workbook(..., data_only=True)`, read only and never saved.

**Step 1 – inspect cheaply (print only small slices).**
```python
from openpyxl import load_workbook
wb=load_workbook('protein_expression.xlsx'); t=wb['Task']; d=wb['Data']
print(d.max_row,d.max_column)
for r in range(1,4): print([d.cell(r,c).value for c in range(1,6)])
for r in range(1,12): print(r,[t.cell(r,c).value for c in range(1,13)])
for r in range(21,43): print(r,[t.cell(r,c).value for c in range(1,6)])
```

Determine the following before writing anything:
- **Orientation of Data.** Are proteins in rows (IDs in column A) and samples in columns (names in row 1), or the reverse? Is there a second ID column, such as a gene name?
- **Exact form of the sample names.** Compare Task row 10 with the Data header. The Data names have prefixes like `MDAMB468_BREAST_TenPx01`. Task row 10 may hold only the suffix or a partial name.
  - If they are partial, use a wildcard MATCH: `MATCH("*"&C$10,Data!$B$1:$AY$1,0)`.
  - First verify in Python that every Task name matches exactly one Data header via endswith/contains. Watch out for TenPx01 vs TenPx010.
  - Also check for stray whitespace or case differences in names and protein IDs.
- **Which columns C–L are Control vs Treated.** Read row 9; the labels may be in merged cells. Note whether each group is contiguous.
- **Layout of rows 23–27 and 31–41.** Read the labels in column A and the headers in rows 23/31.
  - Rows 24–27 most likely have one protein per column B..K, each row being one statistic. Confirm which row is which statistic from the column A labels.
  - Confirm which protein each column B..K refers to. It is probably protein i = row 10+i, mapped to column B+i−1.
  - Check whether column B of rows 32–41 already contains protein IDs.

**Step 2 – write one script.**

Lookup, assuming IDs are in Data!A and sample headers in Data row 1. Use bounded ranges and adjust to the real extents.
```python
for r in range(11,21):
  for c in range(3,13):
    L=get_column_letter(c)
    t[f'{L}{r}']=(f'=INDEX(Data!$B$2:$AY$201,MATCH($A{r},Data!$A$2:$A$201,0),'
                  f'MATCH("*"&{L}$10,Data!$B$1:$AY$1,0))')
```
- Drop the `"*"&` if the names match exactly; an exact match is safer.
- If Data is transposed, swap the roles of the two MATCH calls.

Group statistics: for protein row r = 11..20, the target column is chr(ord('B')+r−11).
- If the groups are contiguous (e.g. Control C:G, Treated H:L), use `=AVERAGE(Task!C11:G11)`, `=STDEV(C11:G11)`, and likewise for H:L.
- If the groups are interleaved, list the cells explicitly: `=AVERAGE(C11,E11,G11,...)` and `=STDEV(C11,E11,...)`.
- Avoid array formulas such as AVERAGE(IF(...)) or STDEV(IF(...)), because openpyxl/LibreOffice handle them unreliably. `AVERAGEIF($C$9:$L$9,"Control",C11:L11)` is acceptable for means only if row 9 holds labels over every column.
- Use STDEV (sample SD, n−1), not STDEVP.
- No log transform is needed; the data are already log2.

Fold change, for row k = 32..41 with protein i = k−31:
- Log2FC: `C{k} = =<TreatedMeanCell>-<ControlMeanCell>`, pointing to the row-26 and row-24 cells in that protein's column (as identified by the labels).
- FC: `D{k} = =2^C{k}`.
- Make sure the protein order in rows 32–41 matches the order in rows 11–20 and B–K. Check the column A/B labels.

Then `wb.save('protein_expression.xlsx')`. Only write values into cells; do not touch fills, fonts or number formats.

**Step 3 – recalc and verify.**
- Run `recalc.py` and require `total_errors: 0`.
- If #N/A appears, the lookup keys don't match. Check the name prefixes and whitespace, or whether the wildcard is unsupported in that context. A fallback is to match on a helper-free exact key.
- Reopen with `data_only=True` and print C11:E12, the row 24–27 values for one protein, and C32:D33.
- Cross-check one protein in pandas: pull its row from Data, compute the means and SD with `ddof=1`, and confirm Log2FC and FC = 2**Log2FC. This is for checking only; never write those numbers into the file.

**Pitfalls.**
- Off-by-one errors between DataFrame and Excel rows.
- Mismatched column letters (for 50 samples plus an ID column the header extends to about AY; confirm `max_column`).
- Merged label cells in row 9.
- Duplicate protein IDs in Data (check uniqueness).
- Empty cells in the stat ranges.
- Never overwrite the template's existing labels.
