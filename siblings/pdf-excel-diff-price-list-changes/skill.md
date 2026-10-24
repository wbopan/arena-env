## Reference notes

- Use `pypdf.PdfReader` for the text PDF and `openpyxl` for the workbooks. Inspect one PDF page and the spreadsheet header cheaply before writing the processing script:
  ```python
  from pypdf import PdfReader
  from openpyxl import load_workbook

  reader = PdfReader("/root/work/price_list_backup.pdf")
  print(reader.pages[0].extract_text()[:1200])

  wb = load_workbook("/root/work/price_list_current.xlsx", read_only=True, data_only=True)
  ws = wb["Prices"]
  print(next(ws.iter_rows(values_only=True)))
  ```
- Process **every** PDF page with `page.extract_text().splitlines()`. A data line has four fields separated by the literal `" | "`; skip the repeated title, header and footer rather than treating them as SKUs. Check malformed or duplicate data lines instead of silently losing them. Remove price thousands separators before conversion.
- Match records by **SKU**, not row position. Preserve SKU as text (including any leading zeros); disregard product and stock. With openpyxl, `ws.iter_rows(values_only=True)` yields cell values; locate the four columns from the header rather than assuming an order.
- For cent-precision comparisons, use `decimal.Decimal` and `quantize(Decimal("0.01"))` on both prices. Convert spreadsheet numeric values via `Decimal(str(value))`, not `Decimal(value)`. Percentage-point values for `Change Pct` are `(new - old) / old * 100`, rounded to two decimals; do not store a fraction or apply Excel percent formatting to that result. Consider an old price of zero before dividing.
- Create a new workbook with `Workbook()`, rename its active sheet to `"Changes"`, and use `sheet.append([...])` for the exact header and affected rows. Sort SKU keys ascending, leave inapplicable cells as `None`, and write price and percentage results as numeric values (e.g. `float(rounded_decimal)`), not formatted strings. `wb.save(path)` writes the `.xlsx`. For a static reconciliation, numeric values avoid openpyxl’s formula-cache limitation: openpyxl writes formulas but does not calculate their displayed results.
- Run the script once, then reopen the output with `load_workbook(..., read_only=True, data_only=True)` to inspect its sheet name, header, row count, ordering, numeric cell types and blank cells.
