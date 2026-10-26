## Reference notes

Use **pandas** to join the three driver CSVs on `Year` and **NumPy** for the specified PCA. Do not include `water_temperature.csv`, use row-position joins, run separate PCAs by category, or use varimax/factor analysis.

```python
from pathlib import Path
import pandas as pd
import numpy as np
import json

root = Path("/root/work")
climate = pd.read_csv(root / "climate.csv")
hydrology = pd.read_csv(root / "hydrology.csv")
land = pd.read_csv(root / "land_cover.csv")
drivers = climate.merge(hydrology, on="Year", validate="one_to_one").merge(
    land, on="Year", validate="one_to_one"
)
```

Select columns in the task’s stated order. For an `N × 8` float array `X`, the required calculations are:

```python
Z = (X - X.mean(axis=0)) / X.std(axis=0, ddof=0)
C = Z.T @ Z / len(Z)                  # covariance with divisor N
eigenvalues, eigenvectors = np.linalg.eigh(C)
order = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[order]
eigenvectors = eigenvectors[:, order] # columns are unit eigenvectors
pc1 = eigenvectors[:, 0]
if pc1[np.argmax(np.abs(pc1))] < 0:
    pc1 = -pc1
```

PC1/PC2 variance percentages are `100 * eigenvalues[i] / eigenvalues.sum()`. For each predefined category, its PC1 share is `100 * sum(pc1[j]**2 for j in its column indices)`; choose the largest. The JSON loadings are the **signed eigenvector entries**, not eigenvalue-scaled correlations. Round numeric output values with `round(float(value), 6)` and write JSON using `json.dump(...)` to `/root/work/pca_summary.json`. Check that selected columns have usable numeric values and nonzero standard deviations before dividing.
