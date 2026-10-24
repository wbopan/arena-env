## Reference notes

- Use Python’s `json`, `math`, `csv`, and `pathlib`; keep optimization indices separate from station IDs. Inspect the input cheaply before choosing an algorithm: count stations, check IDs and targets, and compare `start_load + sum(targets)` with the capacity bounds.
- Read `stations` in input order. Let index `i` identify a station internally; write its original `stations[i]["id"]` to the CSV. Do not assume IDs are consecutive.
- A target `t` is a **signed change in truck load**: pickup `max(t, 0)`, drop-off `max(-t, 0)`. After visiting `i`, `load += t[i]`; require `0 <= load <= vehicle_capacity`. Check the initial load too. Each station is visited once, including zero-target stations.

```python
data = json.loads(Path("/root/work/truck.json").read_text())
stations = data["stations"]
ids = [int(s["id"]) for s in stations]
targets = [int(s["net_rebalancing_target"]) for s in stations]
assert len(ids) == len(set(ids))
```

**Distance:** coordinates are degrees. Use radius **3960.0 miles**, with unrounded great-circle distances throughout optimization:

```python
def miles(a, b):
    p1, p2 = math.radians(a["latitude"]), math.radians(b["latitude"])
    dl = math.radians(a["longitude"] - b["longitude"])
    c = math.sin(p1)*math.sin(p2) + math.cos(p1)*math.cos(p2)*math.cos(dl)
    return 3960.0 * math.acos(max(-1.0, min(1.0, c)))
```

Precompute depot–station and station–station distances. Include **both** depot legs in the objective.

**Choosing a method:** For a small station count, subset dynamic programming can give an exact answer. A state `(visited_mask, last_station)` has load `start_load + sum(targets[i] for i in visited_mask)`, so load need not be another state dimension. Extend only to an unvisited station whose resulting load is in `[0, capacity]`; retain the shortest distance and a predecessor for each state. Compare complete states **after adding the last-station-to-depot distance**. This uses exponential space/time, so check station count first.

If using a binary-arc optimization model instead, require one departure from the depot, one return, and exactly one inbound and outbound arc at every station. Enforce load transitions on selected arcs **and add subtour elimination**: degree constraints alone allow disconnected station cycles. MTZ order constraints are a compact option: for distinct stations `i,j`, `order[i] - order[j] + n*x[i,j] <= n-1`, with each order bounded from 1 to `n`. Do not rely on physical truck load to eliminate subtours; pickups and drop-offs can cancel.

**Output and check:** Follow the chosen order once, recomputing load from `start_load` and each signed target—not from optimizer load variables. Confirm the order contains every internal index exactly once and every load is within bounds. Write with `csv.writer`, supplying exactly:

```python
["position", "station_id", "bikes_picked_up",
 "bikes_dropped_off", "load_after_stop"]
```

Rows use 1-based position, original ID, `max(t, 0)`, `max(-t, 0)`, and the recomputed load. Re-read the CSV to check its header, row count, non-negative integer fields, and station IDs.
