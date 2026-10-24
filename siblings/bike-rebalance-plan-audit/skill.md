## Reference notes

Use Python standard-library `json`, `pathlib`, and `math`. This is an audit of the supplied stop order, **not an optimization problem**; no solver or route construction is needed.

```python
import json
from pathlib import Path

data = json.loads(Path("/root/work/data.json").read_text())
plan = json.loads(Path("/root/work/plan.json").read_text())
stations = data["stations"]
by_id = {s["id"]: s for s in stations}  # IDs are labels, not list indices
```

Look up each stop using `stop["station_id"]`. Preserve `plan["vehicles"]` order and `data["stations"]` order in the respective output arrays. Initialize pickup/dropoff totals for **all** stations, including unvisited ones. Repeated visits count each time.

For distance, use the specified radius and unrounded coordinates in degrees. One great-circle implementation from the routing skill is:

```python
def great_circle_miles(a, b):
    r = math.pi / 180.0
    phi1 = (90.0 - float(a["latitude"])) * r
    phi2 = (90.0 - float(b["latitude"])) * r
    theta1 = float(a["longitude"]) * r
    theta2 = float(b["longitude"]) * r
    cosine = (math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2)
              + math.cos(phi1) * math.cos(phi2))
    return 3960.0 * math.acos(max(-1.0, min(1.0, cosine)))
```

For each vehicle, sum the legs `depot → first stop → … → last stop → depot`; an empty stop list travels zero miles. Keep full precision while summing legs and vehicles, then round reported mile values to four decimals.

Track loads in stop order: start with `start_load`, then add `bikes_picked_up - bikes_dropped_off` at each stop. Compute `min_load`, `max_load`, and `capacity_ok` over the **entire sequence, including the start load**; `end_load` is its last value. Separately aggregate each station’s pickups and dropoffs across vehicles. Station inventory is `initial_bikes - pickups + dropoffs`; unmet amount is `abs(net_rebalancing_target - (pickups - dropoffs))`.

Sum the unrounded vehicle distances and integer unmet amounts for the summary. Compute penalty as `penalty_weight * total_unmet_rebalancing_amount`, and objective as travel distance plus penalty; round reported penalty and objective to four decimals. `all_feasible` requires every vehicle capacity flag and every station inventory flag to be true. JSON flags should be Python `bool` values, counts Python `int` values; write with `json.dumps(...)` to `/root/work/audit.json`.
