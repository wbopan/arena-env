### Reference notes

Use `pandas` for year alignment and annual differences, and `numpy` for Pearson correlation. The driver categories are: Heat (air temperature), Flow (inflow), Wind (wind speed), Human (developed percentage). PCA, regression, trend tests, and R² decomposition do **not** apply: this task asks for separate pairwise correlations.

```python
import pandas as pd
import numpy as np

df = pd.read_csv(path).set_index("Year").sort_index()
changes = df[column].diff()  # change at year t = value[t] - value[t-1]
```

Compute differences **before** restricting to comparison years. Align by `Year`, not CSV row position. For a response-year index `years` and lag `L`, pair:

```python
response = water_changes.loc[years].to_numpy()
driver = driver_changes.reindex(years - L).to_numpy()
r = np.corrcoef(response, driver)[0, 1]
```

Check that both arrays have the expected length and no missing values; `.reindex()` will expose absent years as `NaN`. For each driver, evaluate lags in ascending order and select the largest `abs(r)`, retaining the earlier lag on an exact tie. Keep the **signed** `r`; `abs_r_pct = 100 * abs(r)`. Format both numeric output fields with `f"{value:.6f}"`. Write a CSV with the specified header and category order, using the original input-column names as driver names.
