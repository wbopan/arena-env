## Reference notes

Use **NumPy** for the CW I/Q and FFT processing; `json` and `csv` from the standard library suffice for the sidecars and output. Read each sidecar to get its sample rate and sample count rather than inferring them from the binary length. Interleaved little-endian signed int16 I/Q uses **4 bytes per complex sample**:

```python
import json
import numpy as np

with open(json_path) as fh:
    meta = json.load(fh)
raw = np.fromfile(bin_path, dtype='<i2')
assert raw.size == 2 * sample_count  # sample_count from the sidecar
iq = raw[0::2].astype(np.float64) + 1j * raw[1::2].astype(np.float64)
```

For CW captures, there is no range FFT or range-bin selection. Remove the large constant reflection **before** taking the angle:

```python
phase = np.unwrap(np.angle(iq - iq.mean()))
time = np.arange(len(iq)) / fs          # fs: sidecar sample rate, in Hz
slope, intercept = np.polyfit(time, phase, 1)
residual = phase - (slope*time + intercept)
freq = np.fft.rfftfreq(len(residual), d=1/fs)
power = np.abs(np.fft.rfft(residual))**2
```

Use the task’s **ordinary FFT power**, not the skills’ optional filtering, decimation, or Welch PSD workflow: those change the specified bins and powers. Restrict peak selection to `0.7 <= freq <= 3.0`, including both endpoints. Keep the dominant bin’s unrounded frequency and power for subsequent calculations. If half its frequency is also in that interval, `np.interp(half_frequency, freq, power)` gives the linearly interpolated power; choose the half-frequency only when that power is **strictly greater** than `0.5 * dominant_power`. Multiply the chosen fundamental frequency by 60 for bpm.

Write rows in capture-number order using `csv.writer`, with the exact header `capture_id,dominant_hr_hz,heart_rate_bpm`. Format the *dominant* frequency to four decimal places and bpm to one; do not round frequencies before the harmonic comparison or bpm calculation.
