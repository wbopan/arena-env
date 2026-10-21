# Multi-lake warming trend test

The file `/root/work/lake_temps.csv` holds annual mean lake surface temperature (0-5 m) for several lakes. It is in long format with the columns `lake_id`, `year` and `temp_c` (degrees C).

- Rows are not sorted.
- Some `temp_c` values are missing (empty). Drop those rows.

For each lake, test for a monotonic long-term trend on the series ordered by year.

**Mann-Kendall test**

- S = sum over all pairs i<j of sign(x_j - x_i).
- Var(S) = [n(n-1)(2n+5) - sum_k t_k(t_k-1)(2t_k+5)] / 18. Here t_k are the sizes of the groups of identical temperature values (ties).
- Z = (S-1)/sqrt(Var) if S>0, Z = (S+1)/sqrt(Var) if S<0, and Z = 0 if S=0.
- Two-sided p-value = 2(1 - Phi(|Z|)), where Phi is the standard normal CDF.

**Sen's slope**

- The median over all pairs i<j of (x_j - x_i)/(year_j - year_i), in degrees C per year.
- Use the actual years, so gaps from missing values are included.

**Trend label**

- `"increasing"` if p < 0.05 and Z > 0.
- `"decreasing"` if p < 0.05 and Z < 0.
- Otherwise `"no trend"`.

**Output**

Write `/root/work/trend_summary.json`. It is a JSON object keyed by `lake_id` (string), one entry per lake. Each value is an object with:

- `n`: integer, the number of non-missing years used
- `sen_slope`: float, rounded to 4 decimals
- `p_value`: float, rounded to 4 decimals
- `trend`: one of the three strings above
