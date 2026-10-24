## Reference notes

Use **pandas** to read the CSV and **NumPy** for the specified least-squares periodogram. The supplied Lomb–Scargle notes recommend the method for unevenly sampled stellar-rotation signals, but their `lightkurve` examples do not specify this task’s exact grid, power definition, or amplitude fit. BLS and TLS are for transit-shaped dips, not this calculation.

- Filter `quality == 0` **before** grouping by `star_id`. The time-sorted rows are interleaved, so do not treat consecutive rows as one star. Do not clip outliers, detrend, weight observations, or change the time values.
- Make the grid with `0.05 + 0.0005 * np.arange(3901)`; an endpoint-based `np.arange` can accidentally omit the last frequency.
- At each frequency, fit all **three** columns (sine, cosine, constant) simultaneously. `np.linalg.lstsq` returns coefficients in the design matrix’s column order:

```python
phase = 2 * np.pi * frequency * time
X = np.column_stack((np.sin(phase), np.cos(phase),
                     np.ones_like(time)))
coef = np.linalg.lstsq(X, flux, rcond=None)[0]  # a, b, c
rss = np.sum((flux - X @ coef) ** 2)
```

For each star, compute `tss = np.sum((flux - flux.mean()) ** 2)` once, then compare `1 - rss/tss` across **only the prescribed grid frequencies**. Keep the coefficients from the maximum-power fit: `period_days = 1/frequency` and `amplitude = np.hypot(coef[0], coef[1])`. Equivalently, because TSS is fixed for a star, the minimum-RSS fit wins. Do not substitute a library’s default periodogram grid or normalization.

Write one row per star in ascending `star_id` order. With `csv.writer`, write the exact header and format the numeric fields as `f"{period_days:.4f}"` and `f"{amplitude:.5f}"`. Run the script once, then briefly inspect the output header, row count, and formatting.
