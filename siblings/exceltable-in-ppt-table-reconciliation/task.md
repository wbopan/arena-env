# Reconcile a slide table against its embedded workbook

The presentation `/root/work/budget.pptx` has one slide. The slide contains two things:

- **A native PowerPoint table.** It has a header row `Department, Q1, Q2, Q3, Q4, Total` and one row per department. Numbers are shown as integers with comma thousands separators, for example `12,345`.
- **An embedded Excel workbook.** It is an OLE object stored inside the package under `ppt/embeddings/`. Its first worksheet has the header row `Department, Q1, Q2, Q3, Q4, Total`, followed by one row per department. The department rows may be in a different order than on the slide. The quarter cells hold integer constants. Each Total cell is a `=SUM(...)` formula over that row's quarter cells, and you must evaluate it.

The workbook is the source of truth. Compare every numeric cell of the slide table (Q1, Q2, Q3, Q4 and Total) with the workbook value for the same department and column.

Write `/root/work/mismatches.csv` listing every cell that differs.

- **Header:** exactly `department,column,slide_value,workbook_value`
- **Rows:**
  - `column` is the header name (`Q1`, `Q2`, `Q3`, `Q4` or `Total`).
  - Both values are plain integers with no separators.
- **Order:** follow the slide table's row order (top to bottom). Within a row, follow column order (left to right).
- **Format:** comma-separated, no index column, no quoting unless required.
