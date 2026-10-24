## Reference notes

- Read the commission schedule from **every page** of the PDF before coding its rules:
  ```python
  from pypdf import PdfReader
  for i, page in enumerate(PdfReader("background.pdf").pages, 1):
      print(f"--- page {i} ---\n{page.extract_text() or ''}")
  ```
  PDF text may lose table alignment. Check tier boundaries, rate units (percent versus basis points), the minimum’s scope, and the SELL fee’s calculation and rounding instructions against the extracted text.

- Read the named worksheet with `openpyxl`; its row values preserve Excel numeric cells without requiring DataFrame type inference:
  ```python
  from openpyxl import load_workbook
  ws = load_workbook("data.xlsx", read_only=True, data_only=True)["Trades"]
  rows = ws.iter_rows(values_only=True)
  headers = next(rows)
  # Map column names to positions; process the remaining rows.
  ```
  `data_only=True` reads cached results rather than formula strings if input cells contain formulas. Inspect the header and a few rows cheaply before processing all trades.

- Use `decimal.Decimal` for USD arithmetic, not binary floats. Convert Excel numbers with `Decimal(str(value))`; represent rates and fees from the PDF as decimal strings. For cents, use `amount.quantize(Decimal("0.01"), rounding=...)`, following any rounding rule stated in the PDF.

- Calculation order matters: round `quantity × price` to cents **before** tier selection; tier lower bounds are inclusive; apply the selected rate to the **entire** notional, not just the amount above the bound. Apply the minimum commission as the PDF directs, then add the SELL-only regulatory fee. Round each trade’s combined charge to cents **before** adding it to the client total. Count trades independently of their charges.

- Write CSV using the standard-library `csv` module (`open(..., "w", newline="", encoding="utf-8")` and `csv.writer`). Sort client names before writing; format a Decimal total with `f"{total:.2f}"` for exactly two decimal places, without currency symbols or grouping separators. After running the script, briefly inspect the header and output rows for order, counts, and formatting.
