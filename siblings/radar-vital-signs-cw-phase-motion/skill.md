## Reference notes

Use **NumPy** for the CW I/Q and phase calculations; use the standard-library `json` module for sidecars and output. Inspect the sidecars first: their sample rate, carrier frequency, sample count, and binary layout are authoritative.

- Interleaved I/Q means `I0, Q0, I1, Q1, ...`. For a sidecar specifying little-endian float32 pairs, read with `np.fromfile(path, dtype='<f4')`; for little-endian int16 pairs, use `dtype='<i2'` and convert to floating point before calculations. If the sidecar specifies big-endian, use `'>f4'` or `'>i2'` instead. Honor any stated scale factor.
- Check that the raw array has **twice** the sidecar’s complex-sample count before de-interleaving. Float32 pairs occupy 8 bytes per complex sample; int16 pairs occupy 4.
- The required CW sequence is:
  ```python
  iq = raw[0::2] + 1j * raw[1::2]  # I first
  iq = iq - iq.mean()               # clutter removal before angle
  phase = np.unwrap(np.angle(iq))
  time_s = np.arange(len(iq)) / sample_rate_hz
  slope, intercept = np.polyfit(time_s, phase, 1)  # least-squares line
  residual_phase = phase - (slope * time_s + intercept)
  displacement_mm = residual_phase * (
      299792458 / carrier_frequency_hz
  ) * 1000 / (4 * np.pi)
  ```
  Subtract **both** fitted slope and intercept. The `4π` denominator already accounts for round-trip propagation; do not double the displacement. No range FFT, decimation, or vital-sign filtering is needed.
- Compute RMS as `np.sqrt(np.mean(displacement_mm**2))` and peak-to-peak as `np.max(displacement_mm) - np.min(displacement_mm)`. Convert NumPy scalars to Python numbers and round each to three decimal places before `json.dump`.

Process captures in numeric order and write one JSON array to the specified output path. Each object should contain only the three requested keys. After writing, reopen the JSON to check its structure and values.
