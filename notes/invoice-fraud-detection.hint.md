1. Peek at page 1 of `/root/invoices.pdf` with pdfplumber (field labels), the column names and head of vendors.xlsx (pandas, `dtype=str`), and `head -3` of purchase_orders.csv.
2. Write one script: regex-parse vendor/IBAN/PO/amount per page, normalize names (lowercase, strip punctuation, limited→ltd, corporation→corp), then fuzzy-match with difflib/rapidfuzz (cutoff ~0.8; print scores to tune).
3. Apply the rules in order: Unknown Vendor → IBAN Mismatch (spaces stripped, uppercase) → Invalid PO → Amount Mismatch (>0.01) → Vendor Mismatch.
4. Dump only flagged invoices to `/root/fraud_report.json` with the exact keys, 1-based pages, float amount and `null` for a missing PO, then reload the file to verify.
