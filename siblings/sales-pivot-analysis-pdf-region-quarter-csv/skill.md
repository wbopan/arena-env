## Reference notes

Use `pypdf` for the ledger, `pandas` for the store lookup, and standard-library `decimal` and `csv` for exact two-decimal sums and output. An Excel pivot table is unnecessary: the deliverable is a CSV.

```python
from pypdf import PdfReader
import pandas as pd

reader = PdfReader("/root/work/transactions.pdf")
for page in reader.pages:                 # process every page
    text = page.extract_text() or ""
    for line in text.splitlines():
        # Ignore the repeated "Date Store Category Amount" header.
        # Parse transaction lines; inspect extracted spacing before fixing a pattern.
        ...
stores = pd.read_excel(
    "/root/work/stores.xlsx", sheet_name="Stores",
    dtype={"StoreID": str},
)
```

A transaction pattern should recognize `YYYY-MM-DD`, store ID, one-word category, and a **signed** amount with two decimals. Do not discard negative amounts. Check a small extract and counts of parsed versus nonempty, nonheader lines: PDF text extraction may change whitespace or line breaks. If line-based parsing misses records, match the transaction pattern against each page’s full extracted text instead.

Use `datetime.date.fromisoformat(date_text)` to get `month`; calendar quarter number is `(month - 1) // 3 + 1`. Map `StoreID` to `Region` from the `Stores` sheet. Start with **every distinct region in that sheet**, including regions with no ledger entries, and initialize all four quarter sums to `Decimal("0.00")`. Convert amount strings directly with `Decimal(amount_text)`, not through `float`.

For output, sort regions alphabetically; sum each region’s four quarters for `Total`, then sum region rows for `Grand Total`. Write with `csv.writer(..., newline="")`, the exact requested header, and `f"{value:.2f}"` for each numeric cell. This yields `0.00` for empty cells and no thousands separators.
