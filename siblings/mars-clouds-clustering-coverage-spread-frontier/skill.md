## Reference notes

Use the Python standard library (`csv`, `json`, `itertools`) and NumPy; no clustering package is needed. Read `citsci.csv` with `csv.DictReader`: the columns are `file_rad`, `x`, and `y`. Group rows by `file_rad` while preserving each image’s CSV point order. Do not cluster points from different images together.

For one image and one `shape_weight`, the supplied metric is ordinary Euclidean distance after scaling coordinates:

```python
xy = np.asarray(points, dtype=float)          # rows are [x, y], in CSV order
scaled = xy * [shape_weight, 2 - shape_weight]
delta = scaled[:, None, :] - scaled[None, :, :]
dist = np.sqrt(np.sum(delta * delta, axis=2))
neighbors = [np.flatnonzero(dist[i] <= epsilon) for i in range(len(xy))]
```

`np.flatnonzero` yields indices in CSV order. The diagonal is zero, so each point counts toward its own `min_samples` neighbors. Treat `epsilon` as inclusive.

Implement order-sensitive DBSCAN explicitly: visit starting points in CSV order; expand a cluster through core points (`len(neighbors[i]) >= min_samples`) in neighbor order. Assign an unassigned border point when first reached, and do not move it to a later cluster. A point initially marked noise may subsequently be assigned as a border point. Keep cluster IDs local to each image.

Compute objectives **after** clustering all images for a configuration:

- `coverage = total_assigned / total_input`, including noise in the denominator.
- For each image-local cluster, take the arithmetic centroid of its assigned **original, unscaled** `[x, y]` coordinates. `spread_px` is the sum of ordinary Euclidean point-to-own-centroid distances divided by `total_assigned`; it is not a mean of per-cluster means.

Discard configurations below the coverage threshold or with zero assigned points. On retained configurations, compare unrounded objectives: `a` dominates `b` exactly when

```python
a.coverage >= b.coverage and a.spread_px <= b.spread_px and (
    a.coverage > b.coverage or a.spread_px < b.spread_px
)
```

Thus equal objective pairs remain as distinct configurations. Sort surviving records by `(epsilon, min_samples, shape_weight)`. Only when writing JSON, round `shape_weight`, `coverage`, and `spread_px` to five decimal places; leave `epsilon` and `min_samples` as integers. A compact workflow is: inspect the CSV header and row count, write one script, run it, then inspect the JSON structure and a few records.
