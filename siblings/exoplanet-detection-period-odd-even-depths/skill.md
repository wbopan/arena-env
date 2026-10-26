## Reference notes

Use Python’s `csv` module and NumPy; the periods and epochs are already supplied, so no period search or additional detrending is needed.

- Read both CSVs by header name (`csv.DictReader`); retain candidate-file order and `id` as text. Keep only `quality == 0` rows. For each retained row, set `y = flux / reference` and `w = 1 / sigma**2`. **`sigma` is already the uncertainty of `y`; do not divide it by `reference` again.**
- For candidate period \(P\), epoch \(t_0\), and duration \(D\), the required half-integer tie rule is:
  ```python
  event = np.floor((time - t0) / P + 0.5).astype(np.int64)
  in_window = np.abs(time - (t0 + event * P)) <= D / 2
  odd = (event % 2) != 0       # works for negative event numbers
  ```
  Do not use Python `round` or `np.rint` for event numbers: they round half-integers to even.
- Compute **one** weighted baseline using rows outside both candidates’ windows. For each candidate’s odd/even mean, require its window and **not** the other candidate’s window; overlapping rows contribute to neither candidate’s event means.
- For any selected rows, \(\bar y=\sum(wy)/\sum w\). Depth in ppm is \(10^6(\text{baseline}-\bar y_{\rm event})\). Compute `delta_ppm = abs(odd_depth_ppm - even_depth_ppm)` from **unrounded** depths; classify using the unrounded delta and the inclusive `>= 2000` boundary. Round ppm fields only when writing the CSV.

Write the exact requested header with `csv.writer`, then one row per candidate in input order. A short workflow is: inspect CSV headers and a few rows, write one script, run it, then inspect the output header and rows.
