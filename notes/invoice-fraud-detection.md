**Inputs and how to read them**
- `/root/invoices.pdf` holds one invoice per page. Extract text with pdfplumber:
  `import pdfplumber; pages=[p.extract_text() or "" for p in pdfplumber.open("/root/invoices.pdf").pages]`.
  Page number = list index + 1.
  - Fallbacks: `pdftotext -layout /root/invoices.pdf -`, or pypdf `PdfReader(...).pages[i].extract_text()`.
  - If a page has no text it is scanned. Then use OCR via pytesseract plus pdf2image `convert_from_path`.
- `/root/vendors.xlsx`: read with `pd.read_excel('/root/vendors.xlsx', dtype=str)`. Columns are roughly Vendor ID, Name, IBAN. Check the exact headers first. Use `sheet_name=None` if there may be several sheets.
- `/root/purchase_orders.csv`: read with `pd.read_csv(..., dtype=str)`. Columns are roughly PO Number, Amount, Vendor ID. Convert Amount with `float(str(x).replace(',','').replace('$',''))`.

**Inspect cheaply first** (don't print whole files):
- `python3 -c "import pdfplumber;p=pdfplumber.open('/root/invoices.pdf');print(len(p.pages));print(p.pages[0].extract_text())"`. Look at one or two pages to learn the labels (e.g. "Vendor:", "IBAN:", "PO Number:", "Total/Amount:").
- `python3 -c "import pandas as pd;d=pd.read_excel('/root/vendors.xlsx');print(d.columns.tolist());print(d.head(3));print(len(d))"`
- `head -3 /root/purchase_orders.csv; wc -l /root/purchase_orders.csv`

**Parsing invoice fields**
- Use regexes on the page text, anchored on the labels you observed:
  - `re.search(r'Vendor[^:\n]*:\s*(.+)', t)`
  - `IBAN[^:\n]*:\s*([A-Z0-9 ]+)`
  - `PO[^:\n]*:\s*(\S+)`
  - Amount: `(?:Total|Amount)[^:\n]*:\s*\$?([\d,]+\.?\d*)`
- If a label is followed by an empty line, the PO may be absent. Treat a missing or unmatched PO capture as `None`.
- Check that the regex didn't grab the next label's text.
- Strip whitespace from all captured values.
- For the IBAN comparison, remove spaces and uppercase both sides. In the output, keep the IBAN as it appears on the invoice.

**Fuzzy vendor matching** (from the fuzzy-match skill)
Normalize names before comparing:
```python
def norm(s):
    s=s.lower(); s=re.sub(r'[^\w\s]','',s); s=" ".join(s.split())
    for a,b in [("limited","ltd"),("corporation","corp"),("incorporated","inc"),("company","co")]: s=s.replace(a,b)
    return s
```
Then match in this order:
1. Exact normalized match.
2. Otherwise `difflib.get_close_matches(norm(name), [norm(v) for v in names], n=1, cutoff=0.8)`, or rapidfuzz `process.extractOne(..., scorer=fuzz.ratio)` with a score of at least ~85, if rapidfuzz is installed.

Tune the cutoff by printing each invoice's vendor next to its best match and score. Genuinely unknown vendors (e.g. a completely different name) should fall well below the cutoff; typos and Ltd/Limited variants should fall above it. A cutoff that is too loose turns fraud into false matches.

**Decision logic per page** (first matching rule wins, in this order):
1. No vendor match → "Unknown Vendor".
2. Normalized invoice IBAN ≠ vendor's IBAN → "IBAN Mismatch".
3. PO is None or not among the CSV PO numbers (stripped, exact) → "Invalid PO".
4. `abs(po_amount - invoice_amount) > 0.01` → "Amount Mismatch".
5. PO's Vendor ID ≠ the matched vendor's Vendor ID → "Vendor Mismatch".

The invoice's vendor ID comes from the fuzzy-matched vendor row, unless the invoice shows its own Vendor ID, in which case check that too.

Pitfall: the IDs may be stored as strings like "V001" or as ints. Read with `dtype=str` and strip.

**Output**
- File: `/root/fraud_report.json`. It is a JSON list containing only flagged invoices, sorted by page.
- Each item has these keys, exactly:
  - `invoice_page_number` (int, 1-based)
  - `vendor_name` (string as it appears on the invoice)
  - `invoice_amount` (float)
  - `iban` (string)
  - `po_number` (string, or JSON `null` when the PO is missing)
  - `reason` (exactly one of: "Unknown Vendor", "IBAN Mismatch", "Invalid PO", "Amount Mismatch", "Vendor Mismatch")
- Write with `json.dump(results, open('/root/fraud_report.json','w'), indent=2)`. Python `None` becomes `null`.
- A PO number that appears on the invoice but is not in the CSV stays as that string; only an absent PO becomes null.

**Plan**
1. Inspect the 3 inputs with the one-liners above.
2. Write `/root/solve.py` covering parsing, matching, the rules and the JSON dump.
3. Add a debug print showing, per page: page, parsed fields, best vendor match and score, reason.
4. Run it and scan the debug lines for parse failures (None amounts, garbled names).
5. Validate the output: `python3 -c "import json;d=json.load(open('/root/fraud_report.json'));print(len(d));print(d[:3])"`. Confirm the keys, types and reason strings.
