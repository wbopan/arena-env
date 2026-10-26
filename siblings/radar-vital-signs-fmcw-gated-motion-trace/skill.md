## Reference notes

Use `numpy` for the radar pipeline, `json` for the sidecars, and the standard-library `csv` module for output. Inspect the JSON keys before writing the processing script; use each capture’s own metadata.

- **Input format:** Real-only little-endian signed int16, **2 bytes per ADC sample**. Do not de-interleave I/Q. Check that the sample count equals `chirp_count * samples_per_chirp`.
- **Fast-time FFT:** Consecutive samples form rows of shape `(chirp_count, samples_per_chirp)`. Subtract each row’s mean *before* `np.fft.rfft(..., axis=1)`:
  ```python
  raw = np.fromfile(bin_path, dtype='<i2')
  chirps = raw.reshape(n_chirps, samples_per_chirp).astype(np.float64)
  R = np.fft.rfft(chirps - chirps.mean(axis=1, keepdims=True), axis=1)
  ```
- **Stationary-clutter removal:** Subtract the **complex** temporal mean separately at every range bin, before measuring magnitudes or extracting phase:
  ```python
  R -= R.mean(axis=0, keepdims=True)
  ```
- **Range gate:** Bin `k` has nominal range `k * metres_per_range_bin`. Form an ascending array of bins satisfying `0.3 <= range <= 0.9`, including both endpoints and only bins present in `R`. Score each by `np.abs(R[:, bins]).mean(axis=0)`. `np.argmax` returns the first maximum, so ascending bins break ties toward the lower bin. Use **only that single bin** for phase; do not sum adjacent bins.
- **Slow-time phase and trend:** `phase = np.unwrap(np.angle(R[:, selected_bin]))`. Chirp times are `np.arange(n_chirps) / chirp_rate_hz`. Fit an ordinary least-squares line (for example, `slope, intercept = np.polyfit(times, phase, 1)`) and subtract `slope * times + intercept`. Mean-centering alone is not line detrending. Convert the residual using `phase_rad * (299792458 / carrier_frequency_hz) * 1000 / (4 * np.pi)`. Do not decimate or filter this trace.
- **CSV:** Process captures in numeric filename order. Sample the *fully processed* trace at indices `range(0, n_chirps, chirp_rate_hz)` (ensure the rate is an integer for Python indexing); each row’s `second` is `index / chirp_rate_hz`. Write only `capture_id,second,displacement_mm`, formatting displacement to three decimal places. Check the header, row counts, and first/last sampled seconds after writing.
