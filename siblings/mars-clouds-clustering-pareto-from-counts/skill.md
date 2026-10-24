## Reference notes

Use **pandas** (and optionally numpy); the grid search and DBSCAN are already finished. No clustering or distance calculation is needed.

```python
import pandas as pd
import numpy as np

df = pd.read_csv("/root/work/grid_counts.csv")
print(df.shape, df.head(3).to_string(index=False))  # cheap schema check
```

- Compute metrics **per row before grouping**. Set F1 to zero when `n_matched == 0` (including a zero denominator); set delta to `NaN` for those rows. For matched rows, use `2*n_matched/(n_clusters+n_expert)` and `sum_dist/n_matched`.
- Group by `["min_samples", "epsilon", "shape_weight"]` and take the mean of each metric. `groupby(...).mean()` includes zero F1 rows; pandas means skip `NaN` deltas. Do **not** divide aggregate matches by aggregate counts or average only positive F1 rows.
- Filter on **unrounded** mean F1 with `> 0.5`.

For two kept configurations `a` and `b`, `b` dominates `a` exactly when:

```python
(b_F1 >= a_F1 and b_delta <= a_delta
 and (b_F1 > a_F1 or b_delta < a_delta))
```

Compare every kept configuration against the *other* kept configurations using unrounded means. Equal objective pairs do not dominate each other, so retain both if their configurations differ. Sort survivors by F1 descending, then delta ascending.

Write only columns `F1,delta,min_samples,epsilon,shape_weight`, in that order. Format F1 and delta to five decimal places, shape_weight to one; write min_samples and epsilon as integers. `to_csv(path, index=False)` writes the header. After writing, inspect the header and a few rows without dumping the whole file.
