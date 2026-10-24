## Reference notes

Use Python’s `json`, `csv`, and `numpy`; no optimization solver is needed because generator outputs are fixed. Parse the JSON directly rather than printing the network file.

```python
import json
import numpy as np

with open('/root/work/network.json') as f:
    data = json.load(f)

buses = data['bus']
gens = data['gen']
branches = data['branch']
base = float(data['baseMVA'])
bus_idx = {int(bus[0]): i for i, bus in enumerate(buses)}
slack = next(i for i, bus in enumerate(buses) if int(bus[1]) == 3)
active = [br for br in branches if int(br[10]) == 1]  # preserves order
```

Bus IDs are **not** array indices: map both generator buses and branch endpoints through `bus_idx`. Include every in-service generator at its bus; exclude out-of-service generators and branches.

DC equations, with injections and flows in per-unit:

- \(P_i=(\sum PG_i-Pd_i)/baseMVA\).
- For each active branch \(f\to t\), \(b=1/x\); add `b` to `B[f,f]` and `B[t,t]`, subtract it from `B[f,t]` and `B[t,f]`.
- Set the slack angle to zero. Solve only the **non-slack** rows and columns with `np.linalg.solve(B[np.ix_(keep, keep)], injections[keep])`. The slack injection balances any schedule mismatch; do not prescribe it as an additional equation.
- Signed from-to flow: `flow_MW = (theta[f] - theta[t]) / x * base`.
- `loading_pct = abs(flow_MW) / br[5] * 100`, where column 5 is RATE_A in MW for this task. A zero reactance or zero rating makes these formulas undefined; inspect such data rather than silently substituting zero.

Write active branches in their original order using `csv.writer`, header `from_bus,to_bus,flow_MW,loading_pct`, integer endpoint IDs, and two decimal places for both numeric results (e.g. `f'{value:.2f}'`). Check the output row count against `len(active)` and confirm the non-slack balance residual is small before finishing.
