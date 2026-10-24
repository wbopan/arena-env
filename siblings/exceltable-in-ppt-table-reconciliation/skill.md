## Reference notes

Use `python-pptx` to read the native table, `zipfile` to extract the embedded workbook, `openpyxl` to read its cells and formulas, and standard-library `csv` to write the result. A `.pptx` is a ZIP package; the workbook is under `ppt/embeddings/`. Inspect member names first rather than assuming an embedding filename.

```python
from pptx import Presentation
from zipfile import ZipFile
from io import BytesIO
from openpyxl import load_workbook

prs = Presentation("/root/work/budget.pptx")
table = next(s.table for s in prs.slides[0].shapes if s.has_table)
slide_rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]

with ZipFile("/root/work/budget.pptx") as package:
    names = [n for n in package.namelist() if n.startswith("ppt/embeddings/")]
    # Inspect names; select the Excel workbook member.
    workbook_bytes = package.read(selected_name)

ws = load_workbook(BytesIO(workbook_bytes), data_only=False).worksheets[0]
```

`data_only=False` is important: `openpyxl` **does not evaluate formulas**. Its `Total` cell value will be a string such as `=SUM(B2:E2)`; a cached result, if present, need not be current. Parse that row’s `SUM` range and add the referenced quarter-cell integer values. For example, after obtaining the range reference, `sum(cell.value for row in ws[range_ref] for cell in row)` evaluates a rectangular range. Do not substitute the slide’s quarter values when calculating the workbook total.

Match rows **by department**, not row number; map numeric columns by their header names. Preserve the slide table’s row and column iteration order. Convert slide numbers with `int(text.strip().replace(",", ""))`; workbook quarter cells are integer constants.

Write with `csv.writer(open(path, "w", newline=""))`: its default minimal quoting is suitable. Write the exact four-field header first, then only differing numeric cells, using integers for both output values. After running the script, inspect the CSV header and a few rows for ordering, separators, and unexpected formula text.
