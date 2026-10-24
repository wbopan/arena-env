## Reference notes

Use `numpy` for the allocation and `csv.DictReader` / `csv.DictWriter` for the command and output files. The task does **not** require motor lag, dynamics integration, or controllers.

The relevant motor-model formula is `A @ s = [F, Mx, My, Mz]`, where `s` contains **squared RPM**, not RPM:

```python
A = np.array([
    [ cT,    cT,   cT,    cT],
    [0.0,  d*cT,  0.0, -d*cT],
    [-d*cT, 0.0, d*cT,  0.0],
    [-cQ,    cQ,  -cQ,    cQ],
], dtype=float)

s = np.linalg.solve(A, np.array([F, Mx, My, Mz], dtype=float))
rpm_unconstrained = np.sqrt(np.maximum(s, 0.0))
rpm = np.clip(rpm_unconstrained, rpm_min, rpm_max)
actual = A @ (rpm ** 2)
```

Determine saturation from `rpm_unconstrained` **before** clipping, using strict comparisons (`< rpm_min` or `> rpm_max`). Calculate `actual` from the full-precision clipped RPM; round only when writing CSV.

Inspect the YAML before parsing it. If it consists of flat `key: numeric_value` entries, a small standard-library parser suffices; do not assume a YAML package is installed. Read CSV numeric fields as `float`, retain each `id`, and sort rows by numeric id if the ids are numeric. Write the specified header with `csv.DictWriter`; format RPM to three decimal places, actual force/moments to six, and saturation as `0` or `1`.
