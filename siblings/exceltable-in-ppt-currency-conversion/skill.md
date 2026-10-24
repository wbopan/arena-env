## Reference notes

Use `python-pptx` for slide text, `zipfile` to retrieve the embedded workbook, and `openpyxl` for its first worksheet. A `.pptx` is a ZIP package; the workbook is under `ppt/embeddings/`.

```python
from io import BytesIO
from zipfile import ZipFile
from pptx import Presentation
from openpyxl import load_workbook

slide = Presentation("/root/work/report.pptx").slides[0]
texts = [shape.text for shape in slide.shapes if shape.has_text_frame]
# Find the text whose first line starts "Report currency:"; splitlines()
# preserves the distinction between the header and region lines.

with ZipFile("/root/work/report.pptx") as package:
    names = [n for n in package.namelist() if n.startswith("ppt/embeddings/")]
    # Select the embedded Excel workbook, then:
    wb = load_workbook(BytesIO(package.read(workbook_name)), data_only=False,
                       read_only=True)
    ws = wb.worksheets[0]
```

Check the embedded file type before opening it: `openpyxl` reads OOXML workbooks (`.xlsx`), not an OLE compound-binary `.bin`. Use `data_only=False`: `openpyxl` **does not calculate formulas**, and `data_only=True` only returns saved cached results, which may be absent or stale.

- Matrix orientation matters: row-1 headers (B onward) are **destination** currencies; column-A labels (row 2 onward) are **source** currencies. Look up `rate[source][destination]`, not the reverse.
- For a formula of the specified form `=1/<cell>`, resolve the referenced cell on the same worksheet and calculate `1 / referenced_value`. Allow optional `$` markers in an Excel cell reference. Resolve references recursively if needed; do not assume the opposite matrix entry equals a separately rounded reciprocal. Constants can be read directly from `ws[cell_ref].value`.
- Parse each region line at its colon, retaining the exact region name. Remove commas from the amount before numeric conversion. The report-currency header is not a region.
- Multiply each amount by its source-to-report rate; use `1` when currencies match. Round **each converted amount** to two decimal places before summing. Excel-style rounding of decimal money ties is half away from zero (`Decimal(...).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`); Python’s built-in `round()` uses ties-to-even. Round the sum to two places as well.
- Write JSON with `json.dump`; convert `Decimal` results to numeric `int` or `float` values first, since the standard JSON encoder does not serialize `Decimal` directly. Keep the required keys and every region name.
