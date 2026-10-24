## Reference notes

Use **NumPy** for the supplied `.npz` arrays and Python’s `json` module for output. ObsPy and pretrained phase pickers are unnecessary: the task specifies the AIC calculation exactly.

```python
from pathlib import Path
import json
import numpy as np

for path in Path("/root/work").glob("sta_*.npz"):
    with np.load(path, allow_pickle=False) as record:
        data = record["data"]                 # rows: samples; columns: channels
        dt = float(record["dt"].item())
        channels = str(record["channels"].item()).split(",")
        station = str(record["station"].item())
    column = {name.strip()[-1]: i for i, name in enumerate(channels)}
    z = data[:, column["Z"]]
    n = data[:, column["N"]]
```

For a segment of length `M`, eligible indices are `range(10, M-10)`—the last eligible index is `M-11`. Use `np.var(...)` (population variance, `ddof=0`), natural logarithm `np.log`, and the *specified* right-hand coefficient `M-k-1`, despite the slice `y[k:M]` containing `M-k` samples. `np.argmin` selects the first minimum, satisfying the smallest-`k` tie rule. Do not add an epsilon or substitute a different AIC convention.

```python
def aic_pick(y):
    M = len(y)
    ks = range(10, M - 10)
    scores = [
        k * np.log(np.var(y[:k]))
        + (M - k - 1) * np.log(np.var(y[k:M]))
        for k in ks
    ]
    return 10 + int(np.argmin(scores))
```

Apply it to the **whole Z trace** for `p_idx`. For S, calculate `w = p_idx + round(0.2 / dt)` using that station’s `dt`; apply it to `n[w:]`, then add `w` to convert the segment pick back to a full-trace index. Python’s `round` uses ties-to-even. Calculate elapsed time from the **unrounded** indices and station `dt`; distance is elapsed time times `6.0 * 3.5 / (6.0 - 3.5)`. Select the nearest using unrounded distances, then round the JSON time to 3 decimals and distance to 2. Convert NumPy integers/floats to Python `int`/`float` for `json.dump`.
