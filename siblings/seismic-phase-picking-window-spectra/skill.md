## Reference notes

Use **NumPy** for the `.npz` arrays and FFT, `csv.DictReader` for `windows.csv`, and **openpyxl** for the workbook. ObsPy and phase-picking tools are unnecessary: the sample windows are already specified.

```python
with np.load(path) as record:
    data = record["data"]                 # samples × channels
    dt = float(record["dt"])
    channels = record["channels"].item()  # scalar string or bytes
    if isinstance(channels, bytes):
        channels = channels.decode()
    channels = [name.strip() for name in channels.split(",")]
```

Find column indices from the channel **suffix** (`endswith("Z")`, `"N"`, `"E"`); do not assume column order. Parse CSV indices with `int(...)` and slice every window as `data[start_idx:end_idx, column]`. Python’s slice excludes `end_idx`.

For a window of `n` samples, pair its one-sided coefficients with `np.fft.rfftfreq(n, d=dt)`. Its power array is `np.abs(np.fft.rfft(samples)) ** 2`. For the S spectral fraction, add the N and E **power arrays coefficient by coefficient** before taking the fraction. In each fraction, sum bins where `frequency >= 8`, then divide by the sum of **all** bins, including DC. Do not detrend, taper, normalize, or double FFT bins.

The S horizontal-to-vertical ratio uses time-domain samples: `(sum(N**2) + sum(E**2)) / sum(Z**2)` over the S slice.

Create the `Spectra` sheet with `openpyxl.Workbook()`, append the exact requested header, then append rows in sorted filename order. Use `round(value, 4)` for numeric cell values and save only the requested `.xlsx` path.
