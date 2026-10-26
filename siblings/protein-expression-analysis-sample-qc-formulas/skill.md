## Reference notes

Use **openpyxl** to edit the existing workbook; it preserves sheets, cells, and formulas. Load with `load_workbook(path)` (not `data_only=True`, which reads cached results instead of formulas), create `QC` with `wb.create_sheet("QC")`, and save to the requested output path.

- Inspect the first row of `Data` for sample-column headers and the header row of `Metadata` for `Sample_ID` and `Group`. Build a sample-ID → **1-based Excel column index** mapping; do not assume the two sheets have the same sample order.
- Determine the last protein row from populated IDs in `Data` column A. Avoid relying solely on `max_row` if formatting extends below the data. Measurement ranges start at row 2 and include blanks through that last protein row.
- `openpyxl.utils.get_column_letter(column_index)` converts an index to an Excel letter. A cross-sheet range looks like `'Data'!B2:B100`.
- For each metadata entry, copy its ID and group into `QC` in metadata order. Use Excel formulas on its mapped measurement range:
  - `=COUNT(range)` — numeric measurements, excluding blanks
  - `=AVERAGE(range)` — mean of numeric measurements
  - `=STDEV(range)` — **sample** standard deviation (denominator \(n-1\)); `STDEV.S` is the newer equivalent.
- Set `cell.number_format = "0.0000"` on formula cells in QC columns D and E. This changes display precision, not the underlying formula result.

Minimal API pattern:

```python
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

wb = load_workbook(input_path)
data, meta = wb["Data"], wb["Metadata"]
# Inspect headers; map sample IDs to Data column indices.
# Find the final row containing a protein ID in Data column A.
qc = wb.create_sheet("QC")
qc.append(["Sample_ID", "Group", "Detected_Proteins", "Mean_Log2", "SD_Log2"])
# Iterate Metadata rows in order; construct each mapped 'Data'! range.
# Assign COUNT, AVERAGE, and STDEV formulas; format D/E as "0.0000".
wb.save(output_path)
```

Openpyxl writes formulas but does not calculate their cached values. Check the saved workbook’s QC row count, sample-to-column mapping, range endpoints, formulas, and number formats.
