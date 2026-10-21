# Region x Quarter Sales Matrix from a PDF Ledger

## Inputs

- `/root/work/transactions.pdf` is a multi-page ledger for calendar year 2024.
  - Every page repeats a header line: `Date Store Category Amount`.
  - Each transaction line holds:
    - a date (`YYYY-MM-DD`)
    - a store ID (such as `S03`)
    - a one-word category
    - an amount with two decimals
  - Negative amounts are refunds. They must be included as-is, so they reduce the totals.
- `/root/work/stores.xlsx`, sheet `Stores`, has the columns `StoreID`, `StoreName` and `Region`.
  - Every store ID in the ledger appears in this sheet.

## Task

Build a pivot of total Amount with region as rows and calendar quarter as columns:

- Q1 = Jan-Mar
- Q2 = Apr-Jun
- Q3 = Jul-Sep
- Q4 = Oct-Dec

## Output

Write `/root/work/region_quarter.csv` as comma-separated text:

- The header row is exactly `Region,Q1,Q2,Q3,Q4,Total`.
- Write one row per distinct region found in `stores.xlsx`, sorted alphabetically.
- `Total` is the sum of that region's four quarters.
- The last row has `Grand Total` in the Region column. It holds column sums for Q1-Q4 and for Total.
- Format every number with exactly 2 decimals and no thousands separators, for example `1234.50` or `-12.00`.
- A region-quarter with no transactions is written as `0.00`.
