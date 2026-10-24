## Reference notes

Use **pandas** for CSV joins and **numpy** for OLS; no PCA or factor analysis is needed. The requested contribution removes each *predefined group of original predictors*, not a fitted component.

```python
from pathlib import Path
import pandas as pd
import numpy as np

root = Path("/root/work")
df = pd.read_csv(root / "water_temperature.csv")
for name in ("climate", "hydrology", "land_cover"):
    other = pd.read_csv(root / f"{name}.csv")
    df = df.merge(other, on="Year", how="inner", validate="one_to_one")
```

An inner join retains only years present in all files. `validate="one_to_one"` catches duplicate `Year` keys; inspect the inputs if it raises an error. Create `NetRadiation` by adding `Shortwave` and `Longwave`, then exclude both component columns from every regression. Keep `Year` as a join key, **not** a predictor.

For an OLS model with an intercept, `np.linalg.lstsq` works without an additional regression package:

```python
def r2(data, predictors):
    y = data["WaterTemp"].to_numpy(dtype=float)
    x = data[predictors].to_numpy(dtype=float)
    design = np.column_stack((np.ones(len(data)), x))
    coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)
    residuals = y - design @ coefficients
    return 1 - np.sum(residuals**2) / np.sum((y - y.mean())**2)
```

Use the **same joined observations** for the full model and every reduced model. For each category, remove *all* its columns from the eight-predictor list, then calculate `(R2_full - R2_reduced) * 100`. These are percentage **points**; the four values need not sum to the full-model R². Sort unrounded values descending, then write the specified two-column CSV with values formatted to two decimal places (for example, `f"{value:.2f}"`).
