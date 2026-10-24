## Reference notes

Use `pypdf.PdfReader` for page-by-page text, and standard-library `csv`, `re`, `difflib`, and `decimal` for the audit. No PDF table or form handling is needed.

```python
from pypdf import PdfReader

reader = PdfReader("/root/work/invoices.pdf")
for page_no, page in enumerate(reader.pages, 1):
    text = page.extract_text() or ""
    # Extract this page's four labeled lines.
```

Read `vendors.csv` with `csv.DictReader`; keep rows in **file order** and keep `vendor_id` as a string. Inspect one extracted page and the CSV header cheaply before choosing line-extraction patterns. Anchor patterns to `Invoice No:`, `Vendor:`, `IBAN:`, and `Amount: EUR` so unrelated page text cannot be captured.

- **Name normalization:** lowercase; `re.sub(r'[^a-z0-9\s]', '', name)` (not `\w`, which retains underscores and non-ASCII letters); split into tokens; replace only whole tokens using `{'limited':'ltd', 'corporation':'corp', 'incorporated':'inc', 'company':'co'}`; join with spaces. Normalize both invoice and master names.
- **Resolution:** check normalized exact equality first. Otherwise compare each master name with `SequenceMatcher(None, invoice_norm, master_norm).ratio()`. Retain the first row when scores tie (update the best choice only on `>`), and accept it only at `>= 0.85`. Do not substitute `get_close_matches` or a different similarity metric.
- **Amount:** strip the thousands commas from the captured EUR number. Use `Decimal` or its two-decimal string representation rather than binary floats for duplicate keys; output exactly two decimal places without grouping.
- **IBAN:** remove spaces and uppercase before moving the first four characters to the end. Expand each letter to its decimal value (`A=10` through `Z=35`), then check `int(expanded) % 97 == 1`. The printed groups of four are formatting, not part of the checksum.
- **Duplicates:** process pages in order. Key an earliest-page dictionary by `(vendor_id, amount)` only when the ID is not `UNKNOWN`; look up the key **before** recording its first occurrence. Invoice number and IBAN validity do not affect this comparison.

Write with `csv.writer`, explicitly writing `['page','invoice_no','vendor_id','amount','iban_valid','duplicate_of']`. Emit lowercase string booleans and `''` for no duplicate. After running the script, briefly inspect the header, row count against `len(reader.pages)`, and a few extracted/output rows.
