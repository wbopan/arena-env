## Reference notes

Use Python’s standard-library `json`, `csv`, `cmath`, and `math`; no power-flow solver is needed because bus VM and VA already contain the operating point. Parse the JSON directly rather than printing the file. Bus IDs may be noncontiguous, so map IDs to rows:

```python
import json, csv, cmath, math

with open("/root/work/network.json") as f:
    data = json.load(f)
base = float(data["baseMVA"])
bus_by_id = {int(row[0]): row for row in data["bus"]}
```

For each branch in `data["branch"]`, retain input order and skip it unless `row[10] == 1`. Indices: from/to `[0:2]`, resistance/reactance `[2:4]`, total charging susceptance `[4]`, `RATE_A` `[5]`, tap `[8]`, shift in degrees `[9]`. Bus VM and VA are `[7]` and `[8]`. Construct complex bus voltages with `cmath.rect(VM, math.radians(VA))`.

**MATPOWER pi model, in per unit.** Let `y = 1 / complex(r, x)`, `bc = BR_B`, and `N = tap * cmath.exp(1j * math.radians(shift))`, replacing a zero tap with `1.0`. The from-side transformer changes both its self-admittance and cross-admittance:

```python
Yff = (y + 0.5j * bc) / abs(N)**2
Yft = -y / N.conjugate()
Ytf = -y / N
Ytt = y + 0.5j * bc

I_from = Yff * V_from + Yft * V_to
I_to   = Ytf * V_from + Ytt * V_to
S_from = V_from * I_from.conjugate()  # leaving from bus, pu
S_to   = V_to   * I_to.conjugate()    # leaving to bus, pu
```

If both `r` and `x` are zero, the supplied model notes use `y = 0` to avoid division by zero. Do not treat `BR_B` as the charging at *each* end.

Convert complex powers to MW/MVAr by multiplying by `base`; compute `loss_MW` from the **unrounded** real powers. `RATE_A` is in MVA, so loading is `100 * max(abs(S_from), abs(S_to)) * base / RATE_A` when `RATE_A > 0`, otherwise `0`. Round output quantities to four decimal places only after these calculations; write bus IDs as integers.

Use `csv.writer` with header exactly:

```text
from_bus,to_bus,p_from_MW,q_from_MVAr,p_to_MW,q_to_MVAr,loss_MW,loading_pct
```

Write `/root/work/branch_flows.csv`, then briefly inspect its header and row count against the number of in-service branches.
