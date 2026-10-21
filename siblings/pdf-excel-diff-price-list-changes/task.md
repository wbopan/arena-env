# Price list reconciliation

A purchasing team kept a PDF backup of a supplier price list. Since then they have edited the live spreadsheet without logging the changes.

Inputs:
- `/root/work/price_list_backup.pdf` is the old price list. Each data row reads `SKU | Product | Unit Price | Stock`, with fields separated by ` | `. Prices are in USD and may contain thousands separators (e.g. `1,234.50`). Every page also has a title line, a header row and a page footer.
- `/root/work/price_list_current.xlsx` is the current list. It has a sheet `Prices` with columns `SKU`, `Product`, `Unit Price` and `Stock`. Rows are in no particular order.

Compare the two lists by SKU, looking only at the unit price. Ignore changes to product name and stock.
- `REMOVED`: the SKU is in the PDF but not in the spreadsheet.
- `ADDED`: the SKU is in the spreadsheet but not in the PDF.
- `CHANGED`: the SKU is in both and its unit price differs (compare at cent precision).

Write `/root/work/price_changes.xlsx` with a sheet named `Changes`.
- Row 1 is exactly this header: `SKU`, `Status`, `Old Price`, `New Price`, `Change Pct`.
- Add one row per affected SKU, sorted by SKU ascending, and no other rows.
- Prices are numbers rounded to 2 decimals.
- `Change Pct` = (new - old) / old * 100, rounded to 2 decimals. Fill it only for CHANGED rows.
- Leave `Old Price` empty for ADDED rows and `New Price` empty for REMOVED rows. Leave `Change Pct` empty for ADDED and REMOVED rows.
- Unaffected SKUs must not appear.
