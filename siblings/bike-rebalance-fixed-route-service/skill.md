## Reference notes

The route is fixed: **do not optimize station order or add routing variables**. Use Python’s `json`, `math`, and standard-library collections. A dynamic program indexed by truck load after each stop handles integer service amounts; travel distance is constant across all service choices.

```python
import json
from pathlib import Path

data = json.loads(Path("/root/work/data.json").read_text())
by_id = {s["id"]: s for s in data["stations"]}
ordered = [by_id[sid] for sid in data["route"]]  # retain original IDs in output
```

At station `s`, signed service `q` obeys:

- Station inventory afterward: `initial_bikes - q`, within `[0, station_capacity]`. Thus `-(station_capacity - initial_bikes) <= q <= initial_bikes`.
- Truck load afterward: `load_before + q`, within `[0, vehicle_capacity]`.
- Stop cost: `penalty_weight * abs(net_rebalancing_target - q) + handling_cost_per_bike * abs(q)`.

Initialize the DP at `start_load` with zero cost and an empty service sequence. At each stop, enumerate feasible **integer** `q` for every reachable load and update the resulting load. Retain the lower-cost path for each resulting load; if costs tie within `1e-9`, retain the lexicographically smaller signed-service prefix. Select only the state at `required_end_load` after the final stop. This works because future choices depend on the current load, not on earlier services. Keep unrounded costs throughout.

Compute depot-to-depot distance over `[depot, *ordered, depot]`, using the specified radius and degree-to-radian conversion:

```python
import math

def great_circle_miles(a, b):
    to_rad = math.pi / 180.0
    phi1 = (90.0 - float(a["latitude"])) * to_rad
    phi2 = (90.0 - float(b["latitude"])) * to_rad
    theta1 = float(a["longitude"]) * to_rad
    theta2 = float(b["longitude"]) * to_rad
    cosine = (math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2)
              + math.cos(phi1) * math.cos(phi2))
    return 3960.0 * math.acos(max(-1.0, min(1.0, cosine)))
```

Sum **unrounded** legs. From the selected service sequence, independently reconstruct `loads_after_stops`, `unmet_penalty`, and `handling_cost`; the objective is their unrounded sum plus travel distance. Check every load and station inventory bound and the required final load. Round miles and cost fields to six decimal places only when creating `/root/work/service.json`; include every station ID between `"depot_start"` and `"depot_end"`, including zero-service stops.
