**Goal and outputs (exact):**
- `/root/output/trend_result.csv` has header `slope,p-value` and one data row.
- `/root/output/dominant_factor.csv` has header `variable,contribution` and one data row. `variable` is one of `Heat`, `Flow`, `Wind`, `Human`. `contribution` is a percentage (e.g. `45`, not `0.45`).
- Run `mkdir -p /root/output` first.

**Inspect cheaply (do not cat whole files):**
```
for f in /root/data/*.csv; do echo $f; head -3 $f; wc -l $f; done
python3 -c "import pymannkendall, factor_analyzer, sklearn, scipy; print('ok')"
```
- Identify the time column (Year/Date) and the water temperature column.
- Check whether data are annual or sub-annual. If sub-annual (monthly or daily), aggregate to annual means by year before the trend test.
- Note the shared key column (Year) so the four files can be merged.
- If a library is missing, run `pip install pymannkendall factor_analyzer`.

**Part 1 – Trend (Sen's slope + Mann-Kendall, preferred for environmental data):**
```python
import pymannkendall as mk
r = mk.original_test(wt_values_sorted_by_time)
slope, p = r.slope, r.p
```
- `r.slope` is the change per time step, which is per year if the series is annual.
- The skill says to round results to 2 decimals. Keep enough precision that a tiny p-value does not become `0.0` misleadingly; use `round(x, 4)` or similar.
- The linear-regression alternative is `scipy.stats.linregress(years, values)`. Prefer Sen/MK as the skill advises.

**Part 2 – Classify the variables (domain rules):**
- **Heat:** air temperature, shortwave, longwave, net radiation, humidity, cloud cover, surface temperature.
  - If separate Shortwave and Longwave columns exist, create `NetRadiation = Longwave + Shortwave` and use it in place of the two components.
- **Flow:** precipitation, inflow, outflow, streamflow, evaporation, runoff, groundwater.
- **Wind:** wind speed, direction, gust, air pressure.
- **Human:** developed area, agriculture area, impervious surface, population, land-use change.
- Exclude the year column and the water temperature itself from the predictors.

**Part 2 – Contribution (one global factor analysis, then R² decomposition):**
```python
import pandas as pd, numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from factor_analyzer import FactorAnalyzer
df = wt.merge(clim,on='Year').merge(lc,on='Year').merge(hy,on='Year').dropna()
vars_ = [...all predictor columns...]
X = StandardScaler().fit_transform(df[vars_].values); y = df[WT].values
fa = FactorAnalyzer(n_factors=4, rotation='varimax'); fa.fit(X)
S = fa.transform(X); L = pd.DataFrame(fa.loadings_, index=vars_)
print(L.round(2))
def r2(A): m=LinearRegression().fit(A,y); return m.score(A,y)
full = r2(S)
contrib = [full - r2(np.delete(S,i,axis=1)) for i in range(4)]
```
- **Map factors to categories.** For each factor column, find the variables with the largest |loading| (above 0.7 is strong) and name the factor by their category. Each category should get exactly one factor; resolve ties by the highest loading.
- **Pitfall:** do not run separate PCA per category. Use one global FA with 4 factors and varimax rotation.
- Contribution_i = R²_full − R²_without_i, multiplied by 100.
- The dominant category is the one with the largest contribution. Write `round(contribution_pct)` as an integer percentage.
- Negative or small contributions are normal (suppression/collinearity). Contributions need not sum to R².

**Step-by-step plan:**
1. Inspect headers and row counts and check imports (1–3 commands).
2. Write a single script `/root/solve.py` that:
   - loads the data;
   - computes the trend and writes `trend_result.csv`;
   - merges the files and classifies the variables;
   - runs FA and prints the loadings;
   - maps factors to categories, computes contributions, and writes `dominant_factor.csv`.
3. Run the script. Read the printed loadings and confirm the factor→category mapping makes physical sense. If it doesn't, fix the mapping in the script and rerun.
4. `cat` both output files to verify the exact headers (`slope,p-value` and `variable,contribution`), a single row each, and a percentage value.
