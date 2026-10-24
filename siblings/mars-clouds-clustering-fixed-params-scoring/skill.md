## Reference notes

Use `pandas` for the CSVs, `numpy` for per-image arrays, and `scipy.spatial.distance.cdist` for distances. A generic read preserving image identifiers as strings:

```python
import pandas as pd
from scipy.spatial.distance import cdist

cit = pd.read_csv("/root/work/citsci.csv", dtype={"file_rad": str})
exp = pd.read_csv("/root/work/expert.csv", dtype={"file_rad": str})
```

Iterate over `file_rad` values from **expert.csv**, not just images present in both files. For each image, obtain `[['x', 'y']].to_numpy(dtype=float)` from each table; a missing citizen group is an empty point array.

**Clustering metric:** scale coordinates to `(w*x, (2-w)*y)` before computing ordinary Euclidean distances. This gives the specified anisotropic metric without a Python distance callback. For a nonempty point array:

```python
scaled = points * [w, 2 - w]
dist = cdist(scaled, scaled, metric="euclidean")
neighbors = dist <= eps           # includes each point itself
core = neighbors.sum(axis=1) >= min_samples
```

Find connected components **among core points only**, with `neighbors` defining edges. Assign each non-core point within `eps` of any core point to the component of its *nearest core point* by the anisotropic distance; otherwise discard it as noise. Then take each component’s mean of the **original, unscaled** `(x, y)` coordinates, including assigned non-core members. Do not assume a library’s default DBSCAN border assignment implements this nearest-core rule.

**Matching metric is different:** compute plain, unscaled Euclidean distances between centroids and expert coordinates:

```python
pair_dist = cdist(centroids, expert_points, metric="euclidean")
```

Process *all* centroid–expert pairs in ascending distance order. Accept a pair only when its distance is `<= 100` and both indices are unused. Calculate F1 from the matched count and the two point counts; calculate delta from accepted distances only. With no matches, use `0` for F1 and Python `None` for delta.

Handle empty arrays before distance calculations or indexing. Average F1 across every expert image; average delta only across non-null image deltas. Apply `round(value, 4)` to output floats, and write JSON with `json.dump` (`None` becomes `null`).
