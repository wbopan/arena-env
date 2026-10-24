## Reference notes

Use **pandas** to read the tracks, **NumPy** for ordinary least squares, and the standard-library `json` module for metadata and output. The correspondences are already provided: do not run optical flow, RANSAC, outlier rejection, or temporal smoothing.

For one pair, put two equations per tracked point into a least-squares system with parameter order `[a, b, tx, ty]`:

```python
# x0, y0, x1, y1 are arrays for one pair
A = np.empty((2 * len(x0), 4))
A[0::2] = np.column_stack((x0, -y0, np.ones(len(x0)), np.zeros(len(x0))))
A[1::2] = np.column_stack((y0,  x0, np.zeros(len(x0)), np.ones(len(x0))))
rhs = np.empty(2 * len(x0))
rhs[0::2], rhs[1::2] = x1, y1
a, b, tx, ty = np.linalg.lstsq(A, rhs, rcond=None)[0]
s = np.hypot(a, b)
rot = np.arctan2(b, a)  # radians
```

Group CSV rows by integer `pair`; use **all** rows in each group. Apply the task’s strict `>` thresholds independently: Dolly, Roll, and one translation label can coexist. For translation, horizontal wins a tie (`abs(tx) >= abs(ty)`); vertical requires `abs(ty) > abs(tx)`. Emit `["Stay"]` only if no other label applies. Keep the stated sign conventions even though image y points down.

Read `num_frames` from `meta.json`. Pair `i` labels frame `i`; frame `N-1` repeats frame `N-2`. Compress consecutive identical label sets into maximal **half-open** intervals: key `"start->end"` covers `start` through `end-1`, and the final end is `N`. `json.dump` writes the mapping to the requested `.json` path. Check that pair indices and interval coverage are consecutive, labels are nonempty, and adjacent intervals differ.
