# Regional Revenue Pivot Report

The workbook `/root/work/sales.xlsx` contains one sheet, `Orders`, with the columns `OrderID`, `Region`, `Rep`, `Units` and `UnitPrice`. Each row is one sales order.

Create a new workbook at `/root/work/region_report.xlsx` with exactly these three sheets.

1. **`SourceData`**
   - Row 1 is the header: `OrderID, Region, Rep, Units, UnitPrice, Revenue, SizeBand`, in that order.
   - Below it, write one row per order, in the original order.
   - `Revenue` = Units x UnitPrice, rounded to 2 decimals.
   - `SizeBand` is `Small` if Units < 10, `Medium` if 10 <= Units <= 49, and `Large` if Units >= 50.

2. **`Revenue by Region`**
   - This sheet contains a real Excel pivot table, not static values.
   - The pivot cache source is the `SourceData` sheet. Its range runs from A1 to the last data row in column G.
   - Rows: `Region`.
   - Columns: `SizeBand`.
   - Values: Sum of `Revenue`, using the sum aggregation.

3. **`Region Totals`**
   - A plain static table with the header `Region, Revenue` in row 1.
   - Below it, write one row per distinct region.
   - `Revenue` is the total of that region's `Revenue` values, rounded to 2 decimals.
   - Sort the rows by Revenue in descending order.

Store all numbers as numeric cells, not text.
