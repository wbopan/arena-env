# Lead-lag structure of monthly business-cycle indicators

The input is `/root/work/indicators.csv`, which holds monthly US-style indicators. Its columns are:

- `month` (YYYY-MM)
- `ip_index`: industrial production index
- `payroll_thousands`: nonfarm payroll employment, in thousands
- `unemployment_rate`: in percent

The rows are **not** in chronological order. Sort them by month before doing anything else. There are no missing values.

Steps:

1. **Transform.** Take the natural log of `ip_index` and of `payroll_thousands`. The unemployment rate is already a rate, so keep it in levels and do not log it.
2. **Detrend.** Apply the Hodrick-Prescott filter with λ = 14400 (monthly data) to each of the three series. The trend τ minimizes Σ(y_t − τ_t)² + λ Σ(τ_{t+1} − 2τ_t + τ_{t−1})². The cycle is c = y − τ.
3. **Cross-correlate.** For every lag k from −6 to 6 inclusive, compute the Pearson correlation between IP's cycle at month t and the other series' cycle at month t + k. Use all t for which both t and t + k lie inside the sample, which gives T − |k| pairs. A positive k therefore means the other series lags IP.

Write `/root/work/lead_lag.csv` with these requirements:

- The header is exactly `lag,corr_payroll,corr_unrate`.
- There are 13 data rows, ordered by lag ascending (−6 … 6).
- `lag` is an integer.
- The two correlation columns are rounded to 4 decimal places.
