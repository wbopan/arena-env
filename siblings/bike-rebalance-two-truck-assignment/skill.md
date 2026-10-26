## Reference notes

- Use `json`, `math`, and, for a modest station count, standard-library subset dynamic programming. Inspect the file’s structure and station count first. Station IDs are **not** array indices: keep `ids = [int(s["id"]) for s in data["stations"]]` and map indices back to IDs only when writing routes. Preserve input vehicle order.
- Reject an impossible station before routing: after its required service, inventory is `initial_bikes - net_rebalancing_target`, which must be in `[0, station_capacity]`. A positive target picks up bikes; a negative target drops them off. For a route prefix, truck load is `start_load + sum(targets already serviced)`; check every prefix, including the initial load and final load, against `[0, vehicle_capacity]`.

Use the specified spherical distance, with **unrounded** legs throughout optimization:

```python
import math

def miles(a, b):
    rad = math.pi / 180.0
    p1 = (90.0 - float(a["latitude"])) * rad
    p2 = (90.0 - float(b["latitude"])) * rad
    delta_lon = (float(a["longitude"]) - float(b["longitude"])) * rad
    cosine = (math.sin(p1) * math.sin(p2) * math.cos(delta_lon)
              + math.cos(p1) * math.cos(p2))
    return 3960.0 * math.acos(max(-1.0, min(1.0, cosine)))
```

Precompute depot–station and station–station distances. Do not use distances on latitude/longitude degrees or round individual legs.

**Exact subset-DP option when the station count permits:** For each vehicle separately, let `DP_v[S, j]` be the shortest feasible depot-to-`j` path visiting exactly the index set `S`, with `j ∈ S`. Its load upon reaching `j` is determined by the set alone: `start_load[v] + sum(target[i] for i in S)`. Initialize feasible singleton sets from the depot; extend a feasible state only when the new set’s load is in range. Track the station-ID sequence along with each cost. For each nonempty proper subset `S`, complete vehicle 0’s path back to the depot and vehicle 1’s path for the complement back to the depot. Choose the smallest combined unrounded distance; for distances tied within `1e-9` miles, choose the lexicographically smallest pair of **station-ID** sequences in vehicle order. Neither vehicle may receive the empty set. Subset DP costs exponential time/memory, so check `n` before allocating it.

After choosing routes, independently walk each sequence to recompute loads and both depot-to-depot distances. Confirm every station ID occurs exactly once across the two routes. Write `/root/work/assignment.json` with exactly these top-level keys:

```python
{
    "vehicles": [
        {
            "vehicle_id": ...,  # input value
            "route": ["depot_start", *station_ids_in_visit_order, "depot_end"],
            "loads_after_stops": [...],  # one integer per station visit
            "end_load": ...             # last load
        },
        # second vehicle, in input order
    ],
    "travel_distance_miles": round(unrounded_total, 6),
}
```

`loads_after_stops` excludes both depot labels. Reconstruct the reported distance from coordinates and the final routes, not from a previously rounded objective.
