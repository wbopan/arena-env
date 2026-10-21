# Invoice audit: vendor resolution, IBAN checksums and duplicate payments

Inputs (in `/root/work`):
- `invoices.pdf`: one invoice per page. Each page contains text lines `Invoice No: ...`, `Vendor: ...`, `IBAN: ...` (printed in groups of four) and `Amount: EUR 1,234.56`.
- `vendors.csv`: the approved vendor master, with columns `vendor_id,vendor_name`.

For every page, compute the following:

1. **vendor_id**: Normalize names as follows. Lowercase the name. Delete every character that is not a-z, 0-9 or whitespace. Split on whitespace. Replace the tokens limited->ltd, corporation->corp, incorporated->inc and company->co. Join the tokens with single spaces.
   - If the normalized invoice name equals a normalized master name, use that vendor.
   - Otherwise, find the master vendor with the highest similarity, defined as Python `difflib.SequenceMatcher(None, a, b).ratio()` on the normalized names. On ties, take the first in file order.
   - Use that vendor if the similarity is >= 0.85. Otherwise use `UNKNOWN`.
2. **iban_valid**: Apply the ISO 13616 mod-97 check, ignoring spaces. Move the first four characters to the end, replace letters with numbers (A=10 ... Z=35), and read the result as an integer. The IBAN is valid if that integer mod 97 equals 1.
3. **duplicate_of**: If an earlier page has the same vendor_id (not `UNKNOWN`) and the same amount to the cent, give the page number of the earliest such page. Otherwise leave it empty.

Write `/root/work/invoice_audit.csv` with this header exactly:

`page,invoice_no,vendor_id,amount,iban_valid,duplicate_of`

Format rules:
- One row per PDF page, in page order.
- `page` is 1-based.
- `amount` has two decimals and no thousands separator.
- `iban_valid` is `true` or `false`.
- `duplicate_of` is an integer page number or empty.
