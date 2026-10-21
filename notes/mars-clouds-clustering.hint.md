1. Inspect both CSVs with head/wc and a pandas one-liner (unique `file_rad`, expert images missing from citsci).
2. Write one script: scale coordinates by (w, 2−w) and run sklearn DBSCAN (Euclidean) per image; take centroids from unscaled coordinates, excluding noise.
3. Greedy-match centroids to experts with cdist (≤ 100 px) to get F1 and delta; average over all expert images (F1 zeros included, delta via nanmean). Run the 847-combo grid with joblib and keep F1 > 0.5.
4. Get the frontier with `paretoset(df[['F1','delta']], sense=['max','min'])`. Round F1/delta to 5 decimals and shape_weight to 1, keep min_samples/epsilon as ints, and write `/root/pareto_frontier.csv` with columns `F1,delta,min_samples,epsilon,shape_weight`.
5. Check the file with head: header order, no NaNs, monotonic trade-off.
