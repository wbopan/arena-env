# GCC net-exports distribution statistics

The file `/root/work/trade_long.csv` holds annual data for the six GCC countries in long format. Its columns are `country`, `year`, `indicator`, `unit` and `value`.

The indicators are:
- `gdp_current`: nominal GDP
- `exports_gs`: exports of goods and services
- `imports_gs`: imports of goods and services

The `unit` is either `USD bn` or `USD mn`, and it can differ from row to row. Convert all values to a common unit before computing anything.

For every country-year, compute net exports in percent of GDP:

`NX% = (exports_gs - imports_gs) / gdp_current * 100`

Then, for each year, compute these statistics across the six countries:
- `Min`
- `Max`
- `Median`
- `Mean`: simple mean
- `P25` and `P75`: 25th and 75th percentiles, using the inclusive linear-interpolation definition (Excel `PERCENTILE.INC`)
- `Weighted Mean`: the mean of NX% weighted by each country's share of the six countries' total GDP in that year

Write the results to `/root/work/nx_stats.xlsx` in a worksheet named `Stats`:
- `A1` contains the text `Statistic`.
- `B1` onward contain the years in ascending order, stored as integers.
- `A2:A8` contain these labels, in this order: `Min`, `Max`, `Median`, `Mean`, `P25`, `P75`, `Weighted Mean`.
- Each cell to the right of a label holds that statistic for the year in its column.

Cell values must be in percent, rounded to 3 decimals. They must be stored as plain numbers, not formulas.
