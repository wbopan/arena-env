# PSD estimation and optimal SNR of a template

The file `/root/work/strain.npy` holds raw detector strain with colored noise and one strong instrumental line. It is a 1-D float32 array of 4096 samples at 1024 Hz, in arbitrary strain units. The file `/root/work/template.npy` holds a template waveform. It is a float32 array of the same length and sampling rate. Cast both arrays to float64 before any computation.

1. **PSD.** Estimate the one-sided PSD density of the strain with Welch's method. Use segments of 512 samples, a Hann window, 256-sample overlap, constant (mean) detrending per segment, and mean averaging across segments. This is `scipy.signal.welch` with those settings.
2. **Line.** Find the Welch frequency of maximum PSD among frequencies 20 <= f <= 400 Hz.
3. **Band ASD.** For each band [20,40), [40,80), [80,160) and [160,320) Hz, compute asd = sqrt(mean of the PSD values at Welch frequencies f with f_low <= f < f_high).
4. **Optimal SNR.** Compute h~(f) = rfft(h) / 1024 on the grid f_k = k * 0.25 Hz. Linearly interpolate the Welch PSD onto that grid to get S(f). Then compute:

       rho_opt = sqrt( 4 * sum_{20<=f_k<=400} |h~(f_k)|^2 / S(f_k) * 0.25 )

Write `/root/work/psd_report.json` in this form:

```json
{"line_frequency_hz": 60.0,
 "band_asd": [{"f_low": 20, "f_high": 40, "asd": 0.0123}, ...],
 "optimal_snr": 12.34}
```

List the bands in the order given above. Do not round any values.
