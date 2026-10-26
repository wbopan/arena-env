## Reference notes

Use Python’s `csv` and `json` modules with NumPy. The predicted windows and integer cycle counts are already supplied: **do not run a periodogram, detrend, sigma-clip, or apply additional weighting**.

- Read both CSVs with `csv.DictReader`; convert numeric strings explicitly. Retain light-curve rows only when `int(row["quality"]) == 0`.
- For **each** predicted center, select rows with `abs(time_days - predicted_center_days) <= 0.16`. The boundary is inclusive.
- For each selected row, compute `deficit = max(0.0, 1.0 - flux / reference)`. Its measured center is `sum(time_days * deficit) / sum(deficit)`. The task guarantees a positive denominator.
- Fit measured centers `y` against the corresponding **event numbers** `x`, not their positions in the windows CSV. For unweighted least squares, `period, t0 = np.polyfit(x, y, 1)`; `np.polyfit` returns slope before intercept.
- Calculate residuals from the **unrounded** fit: `r = y - (t0 + period*x)`. Population RMS in minutes is `1440 * np.sqrt(np.mean(r**2))` (not sample standard deviation).
- Round only for output: `round(t0, 6)`, `round(period, 6)`, `round(rms_minutes, 3)`. Write one JSON object with the four specified keys using `json.dump`; convert NumPy scalars to Python `float`/`int` if necessary.

A short workflow: inspect CSV headers and a few rows, write one script to read → measure each center → fit → serialize, run it, then inspect the resulting JSON object.
