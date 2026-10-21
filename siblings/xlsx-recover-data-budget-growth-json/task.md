# Recover missing budget figures and report them as JSON

The file `/root/work/budget_incomplete.xlsx` contains a departmental budget for five departments. Department names are in column A, starting at row 2. The workbook has three sheets.

## Input sheets

- **`Budget`**: columns B-G are FY2019 through FY2024. Each value is an integer budget in USD millions.
- **`YoY (%)`**: columns B-F are FY2020 through FY2024. Each value is the year-over-year change, computed as (Budget_FYn / Budget_FYn-1 - 1) * 100 and rounded to 4 decimals.
- **`Summary`**: this sheet has two value columns.
  - Column B is the FY2019-FY2024 CAGR in percent, computed as ((Budget_FY2024 / Budget_FY2019)^(1/5) - 1) * 100 and rounded to 4 decimals.
  - Column C is the arithmetic mean of the six yearly budgets, rounded to 2 decimals.

Some cells across all three sheets contain the text `???`. Every missing value can be determined from the relationships above. Some missing values depend on other missing values being recovered first.

## Output

Write `/root/work/recovered.json` as a single JSON object.

- Include exactly one entry for each `???` cell and no other entries.
- Each key has the form `<sheet name>!<cell>`, for example `Budget!C3`, `YoY (%)!B4` or `Summary!C2`.
- Each value is a JSON number, rounded as follows:
  - Budget cells: rounded to the nearest integer.
  - YoY and CAGR cells: in percent units (5.25 means 5.25%), rounded to 2 decimals.
  - Average cells: rounded to 2 decimals.
