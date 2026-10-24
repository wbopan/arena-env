## Reference notes

- Use `pandas` to read the workbook and Python’s `json` module to write the result. Row 3 is the header, so `header=2` (pandas uses zero-based header positions):
  ```python
  import pandas as pd
  df = pd.read_excel('/root/work/gdp.xlsx', sheet_name='Data',
                     header=2, dtype={'Series Code': str})
  print(df.columns.tolist(), df.shape)  # cheap layout check
  ```
- The first three columns are `Country`, `Series Code`, and `Series Name`; the remaining year columns may have numeric headers. Convert each year header to a string (for example, `str(int(column))` for numeric years). Ignore blank/non-year columns if present.
- Match **exactly** the suffix after the three-digit country prefix: `code[3:]` must be one of `NGDPD.A` (GDP), `BXGS_BP6.A` (exports), or `BMGS_BP6.A` (imports). Rows can appear in any order; group by country and suffix rather than relying on row positions. Keep country names as they appear in column A.
- For each country-year, calculate the unrounded percentage `100 * (exports - imports) / GDP`. Check for missing inputs with `pd.isna()` and guard against zero GDP rather than silently emitting invalid JSON numbers.
- For each year, calculate the GDP-weighted GCC percentage **before rounding**. Equivalently, `100 * sum(exports - imports) / sum(GDP)` over the six countries. Round country and weighted results to two decimal places only when preparing the output.
- Write the specified nested dictionary with `json.dump(result, file, indent=2, allow_nan=False)`. Read only the input workbook; do not save changes to it. After running the script, briefly inspect the JSON’s country names, year keys, and value types.
