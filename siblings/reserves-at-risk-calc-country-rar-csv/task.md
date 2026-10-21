# Gold Reserves-at-Risk by country

Inputs in `/root/work`:

- `gold_monthly.csv`: columns `period`, `price_usd_per_ozt`. Monthly gold prices from `2024M01` to `2025M09`, in chronological order.
- `reserves.xlsx`: three sheets, each with a `Country` column and year columns `2023`, `2024`, `2025`. Some cells are empty.
  - `Value`: gold reserves in USD millions.
  - `Volume`: gold reserves in millions of troy ounces.
  - `Total Reserves`: total official reserves in USD millions.

Compute for 2025:

1. **Gold value.** If a country has a 2025 figure in `Value`, use it. If a country has no 2025 figure in `Value` (the row is missing or the cell is empty) but does have one in `Volume`, use Volume × the average of the Jan–Sep 2025 monthly prices. Countries with neither figure are excluded.
2. **Volatility.** Compute monthly log returns in percent as `100*ln(P_t/P_{t-1})`. Sigma is the sample standard deviation (n-1 denominator) of the three most recent returns (Jul, Aug, Sep 2025).
3. **Exposure** = gold value × sigma / 100, in USD millions.
4. **RaR** = exposure / 2025 total reserves × 100. Drop any country with no 2025 total-reserves figure.

Write `/root/work/rar.csv` with this header:

`country,gold_value_musd,exposure_musd,total_reserves_musd,rar_pct`

Include one row per remaining country, sorted by `rar_pct` in descending order. Round all numbers to 4 decimals. Country names should appear exactly as in the workbook, with surrounding whitespace stripped.
