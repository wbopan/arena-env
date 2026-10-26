## Reference notes

Use Python’s standard library (`json`, `math`, `pathlib`). For a modest number of stations, subset dynamic programming gives an exact route search without a routing package.

```python
from pathlib import Path
import json, math

data = json.loads(Path("/root/work/data.json").read_text())
stations = data["stations"]
ids = [int(s["id"]) for s in stations]
if len(ids) != len(set(ids)):
    raise ValueError("duplicate station IDs")
```

**Keep IDs separate from indices.** Use `0..n-1` for masks and distance arrays; use the original, nonconsecutive integer IDs in `route` and for lexicographic comparisons.

Coordinates are degrees. Match the specified radius and retain unrounded leg distances:

```python
def miles(a, b):
    r = math.pi / 180.0
    phi1, phi2 = (90.0 - a["latitude"]) * r, (90.0 - b["latitude"]) * r
    theta1, theta2 = a["longitude"] * r, b["longitude"] * r
    cosine = (math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2)
              + math.cos(phi1) * math.cos(phi2))
    return 3960.0 * math.acos(max(-1.0, min(1.0, cosine)))
```

A visited station with target `t` changes **truck load by `+t`** and station inventory by `-t`. Its entire target must be performed. Reject a visit if `initial_bikes - t` is outside `[0, station_capacity]`, or if the resulting truck load is outside `[0, vehicle_capacity]`. An unvisited station costs `penalty_weight * abs(t)`; a visited one has no unmet penalty.

**Exact-search outline:** Start with the empty route. For each reachable state `(visited_mask, last_station)`, retain its best unrounded travel distance and the corresponding sequence of **station IDs**. Extend it only to an unvisited, inventory-feasible station when the new load is feasible. Because targets are fixed, the load for any mask is `start_load + sum(target[i] for i in mask)`, regardless of visit order. Include depot-to-first and last-to-depot legs. Evaluate the empty route too: it travels zero miles and leaves every target unmet. Across completed routes, minimize `travel + unmet_penalty`; for objectives equal within `1e-9`, compare station-ID sequences lexicographically. Compare using unrounded numbers; round only when writing.

Reconstruct distance independently from the selected route, then walk its visits to check load and inventory bounds, uniqueness, and the penalty. Write JSON with **exactly** `route`, `travel_distance_miles`, `unmet_penalty`, `objective`; wrap the station IDs between `"depot_start"` and `"depot_end"` and round the three numeric values to six decimal places.
