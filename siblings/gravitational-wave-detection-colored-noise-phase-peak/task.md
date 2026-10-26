# Phase-sensitive matched-filter peak

Three NumPy files are provided in `/root/work`: `strain.npy` is a 1024-sample float64 detector series, `template.npy` is a real 1024-sample float64 waveform, and `noise_psd.npy` is a positive float64 array of length 513. Samples are spaced by 1/512 second. PSD element k weights frequency bin k of a 1024-point real FFT; use these supplied weights as given, without estimating or interpolating a PSD.

Construct a second, quadrature template as the imaginary part of `scipy.signal.hilbert(template)`. For each of the two templates, form a circular, PSD-weighted correlation series: take `irfft(rfft(strain) * conj(rfft(template_component)) / noise_psd, n=1024)`. Normalize each correlation by the square root of the zero-lag PSD-weighted autocorrelation of that component, calculated with the same FFT convention. At each lag, combine the two normalized correlations by Euclidean magnitude. Search only lags 128 through 895 inclusive; a lag denotes a positive circular shift of the template.

Write `/root/work/phase_peak.json` as UTF-8 JSON with exactly `lag_samples`, `peak_snr`, and `phase_rad`. Select the earliest lag if magnitudes tie. Phase is `atan2(quadrature_correlation, original_correlation)` at that lag, in radians in [-π, π]. Round `peak_snr` and `phase_rad` to six decimal places; `lag_samples` is an integer.
