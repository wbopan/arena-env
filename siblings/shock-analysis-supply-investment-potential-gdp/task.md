# Potential GDP impact of an investment shock

The workbook `/root/work/shock_inputs.xlsx` contains the data for a Cobb-Douglas supply-side model. All money values are in billions of constant USD.

- Sheet `Baseline` has the columns `year`, `K_base` and `lnZ_trend`. There is one row per year from 2024 to 2041. `K_base` is the baseline capital stock and `lnZ_trend` is the log of trend TFP.
- Sheet `Investment` has the columns `year` and `investment`. It lists the extra investment spending by year, and the rows are not sorted. Any year that is not listed has zero investment.
- Sheet `Params` has the columns `parameter` and `value`. It contains `alpha` (the capital share) and `delta` (the annual depreciation rate).

For each baseline year t, in ascending order, compute the following.

- `I`: the extra investment in year t (0 if the year is not listed).
- `dK`: the additional capital stock, dK_t = (1 - delta) * dK_{t-1} + I_t, with dK = 0 before 2024. Investment adds to capital in the same year it is spent.
- `K_with` = K_base + dK.
- `Ystar_base` = exp(lnZ_trend) * K_base^alpha.
- `Ystar_with` = exp(lnZ_trend) * K_with^alpha.
- `gap_pct` = 100 * (Ystar_with / Ystar_base - 1).

Write the results to `/root/work/shock_results.xlsx`, in a sheet named `Shock`.

- Row 1 is the header, exactly: `year, I, dK, K_with, Ystar_base, Ystar_with, gap_pct`.
- Rows 2 onward contain one row per year from 2024 to 2041.
- Cells must hold numeric values, not formulas.
- Round values to 6 decimals or keep full precision.
