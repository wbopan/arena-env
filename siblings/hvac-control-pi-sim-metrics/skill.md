## Reference notes

- Use Python’s standard-library `json`; no fitting, step-test design, or PI retuning is needed. Read `K`, `tau`, `Kp`, and `Ki` directly from `/root/work/params.json`. Keep temperatures and controller state as unrounded floats until calculating the final metrics.
- The first-order room model is `tau * dT/dt + T = T_ambient + K*u`. **Use the task’s explicit Euler update**, not the continuous-time exponential step response.
- Safety takes priority: check `T[k] >= T_max` **before** computing the PI command. A cutoff applies `u = 0`, increments the cutoff count, and does not change `I`. Otherwise, form the candidate integral using the current error; commit it only when the *unclamped* command lies in the inclusive range `0 <= u_raw <= 100`. Clamp the applied command to `[0, 100]` regardless.
- Keep `N + 1` temperatures (including `T0` and the final updated temperature), but only `N` applied heater commands. Evaluate rise and settling times at sample times `k * dt`, not by interpolation. For settling, if the final temperature is in band, the index immediately after the **last** out-of-band temperature is the earliest qualifying index; if none is out of band, it is index 0.
- For steady-state error, `m = max(1, floor(0.2 * (N + 1)))`; with nonnegative lengths, Python’s `int(0.2 * len(temperatures))` gives that floor. The mean heater power uses commands, not temperatures. Round only the output float values to three decimals; write missing times as JSON `null` (Python `None`) and the cutoff count as an integer.

```python
from pathlib import Path
import json

params = json.loads(Path("/root/work/params.json").read_text())
# Simulate into temperatures = [T0, ...] and commands = [u0, ...].
# Calculate metrics from those unrounded sequences.
Path("/root/work/metrics.json").write_text(
    json.dumps(metrics, indent=2) + "\n"
)
```

A short workflow: inspect the JSON once, write and run one Python script, then read the resulting JSON and check its keys, types, and that times are sample times or `null`.
