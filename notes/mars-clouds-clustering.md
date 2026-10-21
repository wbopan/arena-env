**Goal.** Grid-search DBSCAN over 7 × 11 × 11 = 847 combinations, score each one per image against expert points, keep combinations with mean F1 > 0.5, and write their Pareto frontier (maximize F1, minimize delta) to `/root/pareto_frontier.csv`.

**Inspect inputs cheaply (do not print whole files):**
```
head -3 /root/data/citsci_train.csv; head -3 /root/data/expert_train.csv
wc -l /root/data/*.csv
python -c "import pandas as pd;c=pd.read_csv('/root/data/citsci_train.csv');e=pd.read_csv('/root/data/expert_train.csv');print(c.file_rad.nunique(),e.file_rad.nunique(),len(set(e.file_rad)-set(c.file_rad)));print(c.describe())"
```
- Match images directly on `file_rad`. The values are already base names, so no suffix stripping is needed.
- Check that `x` and `y` are numeric and drop NaN rows if any exist.
- Check that `paretoset` and `joblib` import. If they are missing, try `pip install paretoset`, or use the manual Pareto code below.

**Custom metric. Fast and exactly equivalent.** The metric is d(a,b) = sqrt((w·Δx)² + ((2−w)·Δy)²). This equals the plain Euclidean distance after scaling the coordinates as X' = [x·w, y·(2−w)].
- So run `DBSCAN(eps=eps, min_samples=ms).fit(scaled)` with the default Euclidean metric.
- This is identical to passing a Python callable as `metric`, but far faster. Callables, as in the skill doc, work but are slow for 847 combos.
- `min_samples` counts the point itself (sklearn convention); keep the default.

**Centroids.**
- Use labels ≥ 0 only; label −1 is noise and must be ignored.
- Each centroid is the mean of the cluster's ORIGINAL (unscaled) x, y.

**Greedy matching, per image.**
- Compute D = `scipy.spatial.distance.cdist(centroids, expert_pts)` (standard Euclidean).
- Collect all (i, j) pairs with D ≤ 100 and sort them by D ascending.
- Walk the sorted list. Accept a pair if neither centroid i nor expert j has been used yet, then mark both used.
- TP = number of matches.
- precision = TP / n_clusters, recall = TP / n_expert, F1 = 2PR/(P+R).
- delta = mean of the matched distances.
- If the image has no citsci points, no clusters, or TP == 0, set F1 = 0.0 and delta = NaN.

**Aggregation, per combo.**
- Loop over ALL unique `file_rad` in the EXPERT data.
- mean_F1 = plain mean of all per-image F1 values, zeros included.
- mean_delta = `np.nanmean` over the per-image deltas. If every delta is NaN, the result is NaN; such a combo cannot pass the F1 filter anyway.
- Keep the combo only if mean_F1 > 0.5.

**Grid. Avoid float drift.**
```python
min_samples = range(3,10)
epsilons = range(4,25,2)
weights = [round(0.9+0.1*i,1) for i in range(11)]   # 0.9..1.9
```

**Precompute once:**
- `cit = {f: g[['x','y']].to_numpy(float) for f,g in c.groupby('file_rad')}`
- Build the same kind of dict for the experts.
- Pass both dicts to the workers.

**Parallelize** with joblib, one task per (w, eps, ms) combo:
```python
from joblib import Parallel, delayed
res = Parallel(n_jobs=-1)(delayed(evaluate)(ms,eps,w,cit,exp) for ms in ... for eps in ... for w in ...)
```
An alternative is one task per w, looping eps and ms inside the task.

**Pareto frontier** (from the skill): run it on the filtered results using the unrounded values.
```python
from paretoset import paretoset
mask = paretoset(df[['F1','delta']], sense=["max","min"])
front = df[mask]
```
Manual fallback: point A is dominated if some B has B.F1 ≥ A.F1 and B.delta ≤ A.delta, with at least one of the two strict. Keep the points that are not dominated. A vectorized version with numpy over a few hundred rows is trivial.

**Output.**
- Write to `/root/pareto_frontier.csv` with columns exactly `F1,delta,min_samples,epsilon,shape_weight`.
- Round F1 and delta to 5 decimals and shape_weight to 1 decimal.
- min_samples and epsilon must be ints: cast with `.astype(int)`.
- Sort by F1 descending for readability.
- Use `df.to_csv('/root/pareto_frontier.csv', index=False)`.

**Step-by-step plan:**
1. Run the inspection one-liners above.
2. Write `/root/solve.py` containing: load data, build the dicts, define `evaluate(ms, eps, w)` as above, run the joblib grid, filter F1 > 0.5, compute the Pareto mask, round, and save.
3. Run it: `python /root/solve.py`. Print only the number of combos evaluated, the number kept, and the frontier size.
4. Verify:
   - `head /root/pareto_frontier.csv; wc -l /root/pareto_frontier.csv`
   - Check the header order, that there are no NaNs, and that all F1 > 0.5.
   - Check that the frontier is monotonic: as F1 decreases, delta should decrease (non-increasing).
   - Check that shape_weight is printed like `1.2`, not `1.2000000000000002`.
5. Sanity-check one combo by hand, e.g. ms=3, eps=10, w=1.0. Its F1 should be plausible (0 to 1), and the callable-metric DBSCAN should give the same labels on one image as the scaled-coordinate version.

**Pitfalls:**
- Use the standard Euclidean distance (not the custom one) for matching and delta.
- Compute centroids from unscaled coordinates.
- Exclude noise points.
- Include images with no citsci data in the F1 denominator.
- Do not average delta with zeros; use nanmean.
- Use F1 > 0.5 strictly.
- Build the weights by rounding, not with `np.arange`.
