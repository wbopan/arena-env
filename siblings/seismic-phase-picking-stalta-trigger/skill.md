## Reference notes

Use **NumPy** for these `.npz` files; ObsPy and SeisBench are unnecessary. STA/LTA is a short-window energy average divided by a long-window energy average. Use the task’s specified windows and threshold rather than a library trigger routine with potentially different conventions.

```python
from pathlib import Path
import numpy as np

for path in sorted(Path("/root/work").glob("trace_*.npz")):
    with np.load(path) as z:
        data = z["data"]                 # samples × channels
        dt = float(z["dt"])
        channels = str(z["channels"].item()).split(",")
    vertical_col = next(j for j, name in enumerate(channels)
                        if name.strip().endswith("Z"))
    x = data[:, vertical_col].astype(float)
```

Subtract the **whole-trace** mean before squaring: `e = (x - x.mean()) ** 2`. Compute `ns = round(0.5 / dt)` and `nl = round(5.0 / dt)` separately for each file. Python’s `round` supplies the specified sample-count rounding.

For efficient trailing, inclusive windows, a prefix sum with an initial zero lets you obtain the energy sum over indices `i-w+1` through `i` as `prefix[i+1] - prefix[i+1-w]`; divide by `w` for the mean. Consider only `i >= nl-1`, and select the **first** qualifying index. Do not treat an undefined `0/0` ratio as a trigger.

Use `csv.writer` to write the exact header and one row per sorted input path. Use `path.name` for the base name; for a trigger, time is `round(index * dt, 3)`. For no trigger, write `-1` in both numeric columns. Run the script once, then inspect the CSV header, row count, ordering, and numeric formatting.
