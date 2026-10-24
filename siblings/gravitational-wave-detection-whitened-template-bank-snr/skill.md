### Reference notes

Use **NumPy** for this already-whitened, real-valued data. No PSD estimation, filtering, resampling, PyCBC waveform generation, or edge cropping is needed.

```python
import numpy as np

d = np.load("/root/work/data.npy")
bank = np.load("/root/work/templates.npy")  # rows are templates

# For one row h:
rho = np.correlate(d, h, mode="valid") / np.linalg.norm(h)
k_peak = int(np.argmax(np.abs(rho)))
peak_snr = float(abs(rho[k_peak]))
peak_time_s = k_peak / 512
```

`np.correlate(d, h, mode="valid")` computes `sum_j d[k+j] * h[j]` at fully overlapping lags, in increasing lag order. Do **not** reverse the template as for convolution. There are `N-M+1` valid lags; lag `k` denotes the **template start**, not its midpoint or end. `np.argmax` chooses the first lag if peaks tie.

Compute each row’s norm separately: templates are not normalized. Select `best_index` using **unrounded** peak SNRs, then round reported SNRs to 3 decimals and times to 4. Convert NumPy scalars to Python `int`/`float` before writing with standard-library `json.dump`; keep entries in row-index order.
