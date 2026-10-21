# TFP trend estimation for a Cobb-Douglas supply model

The workbook `/root/work/macro_data.xlsx` describes a small open economy.

- Sheet `Macro` has the columns `year`, `K`, `Y` and `CFC`. `K` is the real capital stock, `Y` is real GDP and `CFC` is consumption of fixed capital, all in billions of constant USD. There is one row per year from 2000 to 2023, and the rows are NOT in chronological order.
- Sheet `Params` has the columns `parameter` and `value`. It contains `alpha` (the capital share) and `hp_lambda` (the HP filter smoothing parameter).

After sorting the data by year, compute the following.

1. **Depreciation rate.** For each year, delta_t = CFC_t / K_t. The model depreciation rate is the simple average of delta_t over the 8 most recent years (2016-2023).
2. **Log TFP.** For each year, lnZ_t = ln(Y_t) - alpha * ln(K_t), using natural logs.
3. **HP trend.** Apply the standard Hodrick-Prescott filter to the full lnZ series. The trend tau minimizes sum_t (lnZ_t - tau_t)^2 + lambda * sum_t (tau_{t+1} - 2 tau_t + tau_{t-1})^2, with lambda = hp_lambda.
4. **Trend growth.** trend_growth_last = tau_2023 - tau_2022.

Write the results to `/root/work/supply_trend.json` in this form:

```
{"depreciation_rate": float,
 "trend_growth_last": float,
 "series": [{"year": int, "lnZ": float, "lnZ_trend": float}, ...]}
```

`series` must contain all 24 years in ascending order. Round all floats to 6 decimals.
