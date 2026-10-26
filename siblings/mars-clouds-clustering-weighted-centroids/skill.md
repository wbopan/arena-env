## Reference notes

Use Python’s `csv` module with NumPy/SciPy, or implement the distance check directly. **Do not rely on a library DBSCAN’s traversal order** when border-point ownership must follow the specified CSV visit order.

```python
import csv
import numpy as np
from scipy.spatial.distance import cdist

with open("/root/work/citsci.csv", newline="") as f:
    rows = list(csv.DictReader(f))  # retains CSV order
```

Group by `file_rad` without changing the order of points *within* each group. For one group, keep original coordinates for centroids; scale coordinates only for neighborhood searches:

```python
xy = np.array([(float(r["x"]), float(r["y"])) for r in group])
scaled = xy * np.array([1.5, 0.5])
dist = cdist(scaled, scaled, metric="euclidean")
neighbors = [np.flatnonzero(dist[i] <= 2.5) for i in range(len(xy))]
```

`neighbors[i]` includes point `i`; a **core** point has at least 3 neighbors, counting itself. The radius boundary is inclusive.

For deterministic DBSCAN, scan seed points in CSV order. Skip already visited seeds; mark a new seed visited, and leave it unassigned if non-core. Otherwise create the next cluster ID (starting at 0 for this image) and expand through core points using a FIFO queue and neighbors in CSV order. Assign each reached, unassigned point to this cluster—including non-core points and points previously visited as noise. Never reassign a point already in a cluster. Only core points extend the queue. Keep `visited` separate from cluster assignment so earlier noise can become a border point.

For each cluster, compute `n_points` and arithmetic means from **original** `xy`, including assigned non-core points. Write only clustered rows, sorted by `(file_rad, cluster_id)`, with header exactly:

```text
file_rad,cluster_id,n_points,centroid_x,centroid_y
```

Format centroid values to four decimal places (for example, `f"{mean_x:.4f}"`); write IDs and counts as integers. Read only `citsci.csv`; `expert.csv` must not enter the computation. A short workflow is: inspect the CSV header and a few rows, write one script, run it, then inspect the output header and sample rows.
