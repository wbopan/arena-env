# Gold price volatility table

The workbook `/root/work/gold_prices.xlsx` has a sheet `Prices` with monthly gold prices in US$ per troy ounce. Rows 1-2 hold a title and a source note. Row 3 is the header (`Period`, `Gold`). Data runs from row 4 down, one row per month in chronological order. Periods use IMF style, for example `2022M01`.

Build a volatility table from this series and save it as a new workbook `/root/work/gold_vol.xlsx`. It must contain a sheet named `Volatility` with this exact header in row 1:

`Period | Price | LogReturn | Vol3M | Vol12M | Vol3M_Ann`

Add one data row per input month, starting in row 2, in the same order as the input. Fill the columns as follows:

- `Period`, `Price`: copied from the input.
- `LogReturn`: monthly log return expressed in percent, `100 * ln(P_t / P_{t-1})`. Leave it blank for the first month.
- `Vol3M`: sample standard deviation (n-1 denominator) of the 3 most recent log returns ending at that month. Leave it blank when fewer than 3 returns are available.
- `Vol12M`: the same, using the 12 most recent log returns. Leave it blank when fewer than 12 are available.
- `Vol3M_Ann`: annualized 3-month volatility, `Vol3M * sqrt(12)`. Leave it blank whenever `Vol3M` is blank.

Round all computed values to 6 decimals. Every cell must hold a literal numeric value, not a formula. Blank means an empty cell.
