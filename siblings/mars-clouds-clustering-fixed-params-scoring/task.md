# Mars Cloud Clustering: Scoring One DBSCAN Configuration

Inputs in `/root/work`:
- `citsci.csv`: citizen-science cloud annotations (columns `file_rad`, `x`, `y`; pixel coordinates)
- `expert.csv`: expert annotations (columns `file_rad`, `x`, `y`)

Images are identified by `file_rad`. Evaluate every image that appears in `expert.csv`. Some of these images have no citizen-science points.

## DBSCAN

For each image, cluster its citizen-science points with DBSCAN using these settings:
- min_samples = 4
- eps = 10
- the anisotropic metric d(a,b) = sqrt((w*dx)^2 + ((2-w)*dy)^2), with w = 1.4

Conventions:
- A point is **core** if at least 4 points (itself included) lie at d <= eps.
- Clusters are the connected components of core points, where two core points are linked if d <= eps.
- A non-core point within eps of at least one core point joins the cluster of its nearest core point (nearest by d).
- All other points are noise.
- A cluster's centroid is the mean x and mean y of its members.

## Matching

Match centroids to expert points greedily. Consider all centroid-expert pairs in order of increasing plain Euclidean distance. Accept a pair if neither member is already used and the distance is <= 100.

## Per-image scores

- F1 = 2*n_matched / (n_clusters + n_expert)
- delta = mean Euclidean distance of the matched pairs
- If n_matched = 0, then F1 = 0 and delta = null.

## Output

Write `/root/work/image_scores.json` in this form:

```
{"images": {"<file_rad>": {"n_clusters": int, "n_matched": int, "F1": float, "delta": float or null}, ...},
 "mean_F1": float, "mean_delta": float}
```

- `mean_F1` is the average over all expert images.
- `mean_delta` is the average over images whose delta is not null.
- Round all floats to 4 decimals.
