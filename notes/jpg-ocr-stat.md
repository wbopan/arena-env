**Goal and output format**
- Write `/app/workspace/stat_ocr.xlsx` with exactly one sheet, named `results`.
- Row 1 is the header: `filename`, `date`, `total_amount`. Then one row per image, sorted by filename.
- `filename` is the basename (e.g. `000.jpg`).
- `date` is a string `YYYY-MM-DD`.
- `total_amount` is a string with exactly 2 decimals (e.g. `"47.70"`, no commas). Store it as text, not a float.
- If a field cannot be extracted, leave the cell empty (None). Do not write the text "null".
- No extra rows, columns, sheets or index column. The test compares line by line with an oracle that uses Tesseract plus keyword rules, so follow the task's keyword rules literally rather than being clever.

**Tools**
- Python with `pytesseract`, `PIL`, and `re`.
- Excel output via `openpyxl` or pandas. Check availability first: `python3 -c "import openpyxl, pandas"`.
- OpenAI vision and the PDF skills are not relevant; there is no API and no PDFs.

**OCR**
- Basic call:
  ```python
  text = pytesseract.image_to_string(Image.open(p))
  ```
- Fallback only when a field is missing. Preprocess with `ImageOps.autocontrast(img.convert('L'))` and optionally `.filter(ImageFilter.SHARPEN)`.
- You can also try `config='--psm 6'` or `'--psm 4'`.
- Keep the first successful extraction per field; don't let fallbacks override a default-pass result.
- Process all `.jpg/.jpeg/.png` files in `/app/workspace/dataset/img`, using `sorted(os.listdir(...))`.

**Total amount extraction (from the task hint)**
1. Uppercase each line. Skip any line containing an exclusion word: `SUBTOTAL`, `SUB TOTAL`, `TAX`, `GST`, `SST`, `DISCOUNT`, `CHANGE`, `CASH TENDERED`.
2. Search the keyword groups in priority order, stopping at the first group that yields a value:
   1. `GRAND TOTAL`
   2. `TOTAL RM`, `TOTAL: RM`
   3. `TOTAL AMOUNT`
   4. `TOTAL`, `AMOUNT`, `TOTAL DUE`, `AMOUNT DUE`, `BALANCE DUE`, `NETT TOTAL`, `NET TOTAL`
3. On a matching line, take the last number matching:
   ```python
   num_re = r'\d{1,3}(?:,\d{3})+\.\d{2}|\d+\.\d{2}'
   ```
   Remove commas, then format with `f"{float(v):.2f}"`.
4. If the keyword line has no number, use the last number on the next line.
5. If nothing is found, use None.
6. Consider tolerating OCR noise such as `RM47.70` and `47,70`. Keep it conservative.

**Date extraction**
- Receipts are mostly Malaysian, so dates are day-first.
- Try these regexes in order on the full text:
  - `(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})` → Y-M-D
  - `(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})` → D-M-Y
  - `(\d{1,2})[-/.](\d{1,2})[-/.](\d{2})\b` → D-M-YY, mapping to 20YY
  - `(\d{1,2})[ -]?(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*[ -,]*(\d{2,4})` (case-insensitive)
- Validate each candidate with `datetime.date(y, m, d)`. If invalid, try the next match.
- If day ≤ 12 and the month would be invalid, swap. Output `date.isoformat()`.

**Writing the Excel file**
```python
from openpyxl import Workbook
wb = Workbook(); ws = wb.active; ws.title = "results"
ws.append(["filename", "date", "total_amount"])
for r in rows:
    ws.append([r["filename"], r["date"], r["total_amount"]])  # None -> empty cell
wb.save("/app/workspace/stat_ocr.xlsx")
```
Alternatively, use pandas `df.to_excel(path, sheet_name="results", index=False)` with string dtype.

**Step-by-step plan**
1. Inspect the inputs cheaply:
   ```
   ls /app/workspace/dataset/img | head; ls ... | wc -l
   ```
   Also check that Tesseract is present with `tesseract --version | head -1`.
2. OCR one or two sample images and print only the relevant lines to learn the layout:
   ```python
   python3 -c "...print([l for l in text.splitlines() if re.search('TOTAL|AMOUNT|DATE|/', l, re.I)])"
   ```
3. Write `/app/workspace/ocr.py` containing the OCR, date and total functions, the sorted loop and the xlsx writer. Cache the OCR text in a JSON file so you can re-tune the regexes without re-running OCR, since OCR is slow (a few seconds per image).
4. Run it and print a compact summary: the row count, then the count of None per column.
5. Verify the output:
   ```python
   openpyxl.load_workbook(p).sheetnames == ['results']
   ```
   Also check that the header is correct, the row count equals the image count, the rows are sorted, the totals match `^\d+\.\d{2}$`, and the dates match `^\d{4}-\d{2}-\d{2}$`.
6. For images with None fields, print only their keyword lines, adjust the rules or try a fallback preprocessing pass, then rerun from the cache.
7. Once the format checks pass, run the evaluation or tests if they are provided.

**Pitfalls**
- Never let `TOTAL` match inside `SUBTOTAL`. Exclusions are checked first, per line.
- A "TOTAL QTY" line may contain an integer only; the regex needs `.dd` decimals, so it is ignored.
- Format amounts as strings so Excel doesn't drop the trailing zero.
- Don't print whole OCR outputs; print filtered lines only.
