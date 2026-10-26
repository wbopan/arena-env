## Reference notes

Use NumPy FFTs and `scipy.signal.hilbert`; the supplied PSD needs **no estimation, interpolation, cutoff, or rescaling**.

```python
import numpy as np
from scipy.signal import hilbert

strain = np.load("/root/work/strain.npy")
template = np.load("/root/work/template.npy")
psd = np.load("/root/work/noise_psd.npy")
quadrature = np.imag(hilbert(template))
```

For each real component `h`, use the **same FFT convention** for correlation and normalization:

```python
H = np.fft.rfft(h)
D = np.fft.rfft(strain)
correlation = np.fft.irfft(D * np.conj(H) / psd, n=1024)
autocorrelation_zero = np.fft.irfft(H * np.conj(H) / psd, n=1024)[0]
normalized = correlation / np.sqrt(autocorrelation_zero)
```

`rfft` produces 513 bins for 1024 real samples, matching the PSD. The conjugate belongs on the template spectrum; with this ordering, array index `lag` represents a positive circular template shift. Do not add a separate FFT, sampling-interval, or one-sided-PSD factor to either expression.

Combine the **two normalized** series with `np.hypot(original_normalized, quadrature_normalized)`. Search the inclusive interval 128–895 using the slice `[128:896]`; `np.argmax` returns its first maximum, giving the earliest tied lag. Compute phase from the two normalized correlations at that lag with `np.arctan2(quadrature_value, original_value)`.

When writing JSON, convert NumPy scalars to Python `int`/`float`; round the two floating-point fields to six decimal places.
