## Reference notes

Use `numpy` and `pandas` for this **fixed-grid weighted box search**, and standard-library `json` for output. Generic BLS/TLS periodograms search or optimize different grids and objectives; they do not directly implement the specified trial order and 40 epochs.

```python
light = pd.read_csv("/root/work/lightcurve.csv")
trials = pd.read_csv("/root/work/trials.csv")  # preserves file order
good = light.loc[light["quality"] == 0]
t = good["time_days"].to_numpy()
y = (good["flux"] / good["reference"]).to_numpy()
w = 1.0 / good["sigma"].to_numpy()**2
tmin = t.min()
```

For each supplied `(P, duration)` **in file order**, visit `j = 0, …, 39` in increasing order. Set `epoch = tmin + j*P/40`. The signed circular offset and inclusive transit mask can be computed as:

```python
offset = ((t - epoch + P/2) % P) - P/2
inside = np.abs(offset) <= duration/2
```

For each mask, sum weights separately inside and outside. If either sum is zero, its weighted mean and score are undefined; skip that combination. Otherwise:

- `mean_in = sum(w[inside] * y[inside]) / sum(w[inside])`, analogously for outside.
- `depth = mean_out - mean_in` (a dip has positive depth).
- `score = depth / sqrt(1/W_in + 1/W_out)`.

Compare **unrounded** scores, updating the best combination only on a strictly greater score. That preserves file-order, then increasing-`j` tie precedence. Do not add outlier removal, flattening, uncertainty rescaling, or extra period/epoch searches: the reference model and exact sampling rule are already specified.

Write one JSON object with Python numeric values (not NumPy scalars), rounding the selected period and epoch to 5 decimals, depth to 6, and score to 3. A short workflow is: inspect CSV headers/row counts cheaply, run one script, then open the JSON to check its field names and numeric types.
