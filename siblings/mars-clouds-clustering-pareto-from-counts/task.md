# Mars Cloud Clustering: Pareto Frontier from Per-Image Match Counts

A DBSCAN hyperparameter grid has already been run on Mars cloud annotations. The results are in `/root/work/grid_counts.csv`, with one row per (configuration, image). Columns:
- `min_samples`, `epsilon`, `shape_weight`: the configuration
- `file_rad`: the image
- `n_clusters`: number of clusters found
- `n_expert`: number of expert points in the image
- `n_matched`: number of matched cluster-expert pairs
- `sum_dist`: sum of the Euclidean distances of the matched pairs, in pixels

Every configuration has a row for every image, including images that have no citizen-science data.

## What to compute

For each configuration (min_samples, epsilon, shape_weight):
1. Per image, compute F1 = 2*n_matched / (n_clusters + n_expert) and delta = sum_dist / n_matched. If n_matched = 0, F1 = 0 and delta is undefined.
2. Mean F1 is the average of per-image F1 over all images, zeros included. Mean delta is the average of per-image delta over the images where it is defined.
3. Keep only configurations with mean F1 > 0.5.

Among the kept configurations, find the Pareto frontier that maximizes mean F1 and minimizes mean delta. A configuration is excluded if another kept configuration has F1 >= and delta <= its values, with at least one of the two strictly better. Use unrounded values for both the filtering and the dominance check.

## Output

Write `/root/work/pareto.csv`:
- Header: `F1,delta,min_samples,epsilon,shape_weight`
- One row per frontier configuration.
- Sort by F1 descending; break ties by delta ascending.
- Round F1 and delta to 5 decimals and shape_weight to 1 decimal. Write min_samples and epsilon as integers.
