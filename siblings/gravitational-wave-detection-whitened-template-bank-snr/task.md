# Matched-filter search over a small template bank

A short stretch of **already whitened** gravitational-wave detector strain is stored in `/root/work/data.npy`. It is a 1-D float64 array of N = 2048 samples at a sampling rate of 512 Hz, so it lasts 4 s. Sample n is at time n/512 s. Whitened noise is stationary, zero-mean and has unit variance per sample.

A template bank of chirp waveforms is stored in `/root/work/templates.npy`. It is a float64 array of shape (6, 128). Row i is template i, already whitened, sampled at the same rate. The templates are **not normalized**.

For each template h_i, of length M = 128, compute the real SNR time series over all fully overlapping lags k = 0 .. N-M:

    rho_i(k) = sum_{j=0}^{M-1} d[k+j] * h_i[j] / sqrt( sum_j h_i[j]^2 )

The peak SNR of template i is max_k |rho_i(k)|. Its peak time is k_peak / 512 seconds, where k_peak is the lag that attains the maximum and marks the template start.

Write `/root/work/results.json` in this form:

```json
{"templates": [{"index": 0, "peak_snr": 3.217, "peak_time_s": 1.2344}, ...],
 "best_index": 2}
```

- `templates` has one entry per template, sorted by `index` (0-5).
- `peak_snr` is rounded to 3 decimals.
- `peak_time_s` is rounded to 4 decimals.
- `best_index` is the index of the template with the largest peak SNR.
