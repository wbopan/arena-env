## Reference notes

Use Python’s `json` and, for the one-dimensional dispatch calculation, `scipy.optimize.brentq`. Parse the file directly with `json.load`; a large JSON file need not be inspected line by line. `baseMVA` is not needed here: the specified PD, limits, outputs, and cost function all use MW.

```python
with open("/root/work/network.json") as f:
    data = json.load(f)

load = sum(bus[2] for bus in data["bus"])  # MW
for i, (gen, cost) in enumerate(zip(data["gen"], data["gencost"])):
    bus, status, pmax, pmin = int(gen[0]), int(gen[7]), gen[8], gen[9]
    c2, c1, c0 = cost[4:7]  # type 2, NCOST=3
```

Match each `gen` row to the `gencost` row **at the same index**. Ignore `gen[1]` (stale PG). An out-of-service row has output zero and contributes neither cost nor spinning margin. Startup and shutdown fields are not part of the stated hourly polynomial cost.

For an in-service unit with positive quadratic coefficient, equal marginal costs give its output at a candidate system price λ:

```python
from scipy.optimize import brentq

def output_at_lambda(lam, c2, c1, pmin, pmax):
    return min(pmax, max(pmin, (lam - c1) / (2 * c2)))
```

Check feasibility first: the load must lie between the sums of in-service PMIN and PMAX. Then find λ so the sum of `output_at_lambda(λ, ...)` equals the load. Marginal costs `2*c2*pmin + c1` and `2*c2*pmax + c1` across in-service units provide a bracket for `brentq` when coefficients are positive and a unit is free. If coefficients are not positive, do not divide by `2*c2`; use a bounded constrained optimizer such as `scipy.optimize.minimize` with equality constraint `sum(P) - load == 0`, and obtain λ from a unit strictly inside its limits.

Compute cost as `sum(c2*P**2 + c1*P + c0)` over in-service units only. Compute spinning margin as `sum(pmax - P)` over those same units. Use **unrounded** dispatch values for cost, margin, and marginal-price calculations; round only when constructing the requested JSON fields. Generator IDs are 1-based row indices, in original file order. Write with `json.dump`.
