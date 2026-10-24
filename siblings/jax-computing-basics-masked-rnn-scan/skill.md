## Reference notes

Use **NumPy** for this recurrence. The documented `jax_skills.rnn_scan(seq, Wx, Wh, b)` has no `h0` or lengths argument, so it does not directly implement the required initial states and masking.

```python
import numpy as np
from pathlib import Path

root = Path("/root/work")
seq = np.load(root / "seq.npy")
lengths = np.load(root / "lengths.npy")
with np.load(root / "rnn_params.npz") as params:
    Wx, Wh, b, h0 = (params[k] for k in ("Wx", "Wh", "b", "h0"))

# After constructing the float64 (B, T, H) output:
np.save(root / "hseq.npy", output)
```

- `.npz` is keyed: retrieve arrays by their exact key names. `.npy` holds one array.
- Check compatible dimensions: `seq.shape == (B, T, D)`, `Wx.shape == (D, H)`, `Wh.shape == (H, H)`, `b.shape == (H,)`, `h0.shape == (B, H)`, and `lengths.shape == (B,)`.
- For each sequence, start the running state at its `h0` row. At each **valid** time step, update it with `np.tanh(x @ Wx + h @ Wh + b)` and store that state. Matrix products use row-vector `@` matrix.
- Initialize the output with `np.zeros((B, T, H), dtype=np.float64)`. Visit only `t < lengths[i]` for sequence `i`; leave later positions untouched so they remain **exactly** zero. Do not round or cast to float32.
- Run the script once, then cheaply inspect the saved array’s shape, dtype, and padded region.
