## Reference notes

Use **pandas** to read and group the CSV, **`scipy.stats.linregress`** for ordinary least-squares regression with an intercept, and the standard-library **`json`** module for output. PCA, factor analysis, and Mann–Kendall methods do not apply here.

```python
import pandas as pd
from scipy import stats

df = pd.read_csv(path)
df["TempC"] = pd.to_numeric(df["TempC"], errors="coerce")
df = df.dropna(subset=["TempC"]).copy()  # empty temperatures are not zero

monthly_mean = df.groupby("Month")["TempC"].transform("mean")
df["anomaly"] = df["TempC"] - monthly_mean
df["time"] = df["Year"] + (df["Month"] - 0.5) / 12
```

Assign seasons from the **calendar month**: DJF = 12, 1, 2; MAM = 3–5; JJA = 6–8; SON = 9–11. Keep December in its recorded year. For each season, pass **all individual available anomalies**, not annual or seasonal averages, to:

```python
result = stats.linregress(season_rows["time"], season_rows["anomaly"])
slope = result.slope       # degrees C per year
p_value = result.pvalue    # two-sided test of zero slope by default
```

Classify using the **unrounded** slope and p-value: `p_value < 0.05` with positive slope → `warming`; with negative slope → `cooling`; otherwise → `no_trend`. Round numeric values only when preparing the JSON. Build the four seasonal objects in the required order and use `json.dump(...)` to write the requested object.
