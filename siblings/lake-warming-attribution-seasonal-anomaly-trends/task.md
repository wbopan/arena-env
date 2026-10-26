# Seasonal trends after removing the monthly cycle

`/root/work/monthly_water_temperature.csv` contains surface-water observations for one lake from 2001 through 2024. Its columns are `Year`, `Month` (1–12), and `TempC` (degrees C). Rows are unsorted, and an empty `TempC` denotes a missing observation. Exclude missing observations rather than treating them as zero. There is at most one observation for each year and month.

For every calendar month separately, calculate the mean of its available temperatures across all years. Subtract that month-specific mean from each available observation to obtain a temperature anomaly. Assign each anomaly to DJF for months 12, 1, 2; MAM for 3–5; JJA for 6–8; or SON for 9–11. December remains in its stated calendar year; do not move it into the next year.

Within each season, regress all of its individual anomalies against decimal time `Year + (Month - 0.5) / 12` using ordinary least squares with an intercept. Report the slope in degrees C per year and the two-sided p-value for a zero slope. Classify a season as `warming` if p < 0.05 and slope > 0, `cooling` if p < 0.05 and slope < 0, or `no_trend` otherwise.

Write exactly `/root/work/seasonal_trends.json`. It must be an object with `unit` equal to `C_per_year` and `seasons` equal to an array of four objects in DJF, MAM, JJA, SON order. Each seasonal object has exactly `season`, `slope`, `p_value`, and `trend`. Round slopes and p-values to six decimal places.
