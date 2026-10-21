# Recover missing cells in a sales grid

The file `/root/work/sales_incomplete.xlsx` has one sheet, `Quarterly Sales`, which occupies the range A1:F10.

- Row 1 holds the headers `Region`, `Q1`, `Q2`, `Q3`, `Q4` and `Total`.
- Rows 2-9 hold eight regions.
- Row 10 is labeled `Total`.
- Every number is an integer sales amount in USD thousands.

The grid follows these accounting rules:

- In each row 2-10, column F equals the sum of columns B-E in that row.
- In each column B-F, row 10 equals the sum of rows 2-9.
- Cell F10 is the grand total and satisfies both rules.

Some cells in B2:F10 contain the text `???` in place of a number. The constraints above determine every missing value uniquely. Some missing values can only be determined after other missing values have been recovered.

## Output

Create `/root/work/sales_recovered.xlsx` with these properties:

- It has the same sheet name (`Quarterly Sales`) and the same layout as the input.
- Every cell that did not contain `???` keeps exactly its original value, including labels and headers.
- Each `???` is replaced by its recovered integer value.
- Recovered values are stored as numeric cell values. Text strings and Excel formulas are not accepted.
- No `???` remains anywhere in the workbook.

After recovery, every row and column constraint listed above must hold exactly.
