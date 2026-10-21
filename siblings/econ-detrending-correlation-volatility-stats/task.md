# Business-cycle volatility of consumption and investment

Inputs in `/root/work`:

- `pce_nominal.xlsx`: nominal personal consumption expenditures in billions of dollars, sheet `Table`. Title and notes rows come first, then a header row. Column A is "Year or quarter" and column B is the total. Annual rows use the integer year as their label. Quarterly rows near the bottom are labelled like `2023: II`. A source footnote row ends the table.
- `pfi_nominal.xlsx`: nominal private fixed investment, with the same layout (column B is the total).
- `cpi_monthly.csv`: monthly CPI, with columns `observation_date` (YYYY-MM-DD) and `CPIAUCSL`.

For each year from 1980 to 2024 inclusive:

1. **Nominal value.** Take it from the annual row. 2024 has no annual row, so use the mean of its available quarterly rows.
2. **Annual CPI.** Use the mean of that calendar year's monthly observations. 2024 is partial, so use the months that are present.
3. **Real value.** Compute nominal / CPI × 100.
4. **Cycle.** Take the natural log of each real series. Apply the Hodrick-Prescott filter with λ = 100 (annual data). The trend τ minimizes Σ(y_t − τ_t)² + λ Σ(τ_{t+1} − 2τ_t + τ_{t−1})². The cycle is y − τ.

Write `/root/work/cycle_stats.json` containing one object with these fields:

- `n_years` (integer): the number of years used.
- `std_pce_pct`, `std_pfi_pct`: the sample standard deviation (ddof = 1) of each cycle, multiplied by 100 (percent).
- `relative_volatility`: `std_pfi_pct / std_pce_pct`.
- `corr`: the Pearson correlation between the two cycles.

Round every float to 4 decimal places. Compute `relative_volatility` from unrounded values.
