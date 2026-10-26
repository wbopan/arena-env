## Reference notes

Use **NumPy** for the `.npy` array and calculations, **SciPy Signal** for conditioning, and the standard-library **json** module for output. The supplied PyCBC examples use different filtering and resampling routines; use the SciPy calls specified in the task instead.

```python
import numpy as np
from scipy.signal import butter, sosfiltfilt, resample_poly

x = np.load("/root/work/raw_strain.npy")  # NumPy array; retain float64
sos = butter(4, 35, btype="highpass", fs=1024, output="sos")
filtered = sosfiltfilt(sos, x)              # default padding; zero-phase
resampled = resample_poly(filtered, 1, 2)  # default window and padding
cropped = resampled[64:-64]                 # crop *after* resampling
```

- `fs` gives `butter`’s cutoff in Hz. `output="sos"` supplies the second-order sections expected by `sosfiltfilt`.
- For each consecutive 224-sample block, RMS is `np.sqrt(np.mean(block ** 2))`. Compute from unrounded samples, then round each amplitude to six decimal places.
- `np.argmax(np.abs(cropped))` returns the **first** index on a tie. Obtain the absolute peak amplitude from that index before rounding.
- Convert NumPy scalars to Python `int` or `float` for `json.dump`; JSON arrays can be ordinary Python lists. Write one UTF-8 file with only the requested keys.
