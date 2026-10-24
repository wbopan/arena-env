## Reference notes

The supplied skills concern repository installation and PDFs; neither is needed here. Use **NumPy** for the `.npz` arrays and Python’s standard-library `json` for output.

```python
import json
import numpy as np

with np.load("/root/work/tokens.npz") as data:
    logps = data["per_token_logps"].astype(np.float64)
    labels = data["labels"]

mask = labels != -100
counts = mask.sum(axis=1)
# Sum only valid positions; divide each row by its own count.
row_avgs = np.where(mask, logps, 0.0).sum(axis=1) / counts
```

- Check that the row count is even; `B = row_avgs.shape[0] // 2`. Chosen averages are `row_avgs[:B]`; rejected averages are `row_avgs[B:]`. Pair these arrays elementwise, **not** as alternating rows.
- Use the task’s stated order of operations: subtract `gamma_beta_ratio` from the average-log-probability difference, multiply that logit by `beta` inside the hinge, then clamp the loss at zero with `np.maximum`.
- Reward accuracy uses a **strict** `chosen_reward > rejected_reward` comparison. Take means over pairs, not over tokens.
- Convert NumPy scalars to Python `float` before JSON serialization; use `round(float(value), 6)` for each output number. For the loss vector, preserve pair order when calling `.tolist()` or iterating. Write with `json.dump(...)`.
