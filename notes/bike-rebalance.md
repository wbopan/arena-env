**Goal.** Solve a pickup/dropoff VRP for bike rebalancing as a MIP with PySCIPOpt. Then write `/root/report.json`, or write next to `data.json` if the task directory differs. Check where `data.json` lives with `ls /root`.

**Inspect cheaply (do not cat the whole file):**
```
python3 -c "import json;d=json.load(open('/root/data.json'));print({k:(v if not isinstance(v,list) else len(v)) for k,v in d.items()});print(d['stations'][0])"
python3 -c "import pyscipopt;print(pyscipopt.__version__)"
```
Confirm these key names: `vehicle_count`, `vehicle_capacity`, `penalty_weight`, `depot` (with latitude/longitude), and `stations`. Each station should have `id`, `latitude`, `longitude`, `initial_bikes`, `station_capacity` and `net_rebalancing_target`. Adapt the script to whatever names actually appear. Never assume station IDs are 0..n-1. Map them with `id_to_idx`, use indices inside the model, and report the original IDs.

**Distance (exact metric, R = 3960.0, miles).** Use the spherical law of cosines:
```python
def gc(a,b,R=3960.0):
    r=math.pi/180; p1=(90-a[0])*r; p2=(90-b[0])*r
    c=math.sin(p1)*math.sin(p2)*math.cos((a[1]-b[1])*r)+math.cos(p1)*math.cos(p2)
    return math.acos(max(-1,min(1,c)))*R
```
- Pass the (lat, lon) values in degrees.
- Do not round distances inside the model.

**Model (PySCIPOpt).**
- Nodes: `START="depot_start"`, `END="depot_end"`, and stations `0..n-1`.
- Arcs: every (i, j) with i in [START]+stations and j in stations+[END], with i != j. Exclude the (START, END) arc, because a vehicle must visit at least one station.
- Arc variables: binary `x[v,i,j]` for each vehicle v in range(vehicle_count).

Route constraints for each vehicle v:
- `sum_j x[v,START,j] == 1`
- `sum_i x[v,i,END] == 1`
- For each station i: incoming == outgoing, and outgoing <= 1. This means each vehicle visits a station at most once.
- Different vehicles may visit the same station (split service is allowed). Do NOT add a global single-visit constraint.

Subtour elimination (MTZ):
- Order variables: `order[v,i]`, continuous, in [1, n].
- For station pairs i != j: `order[v,i] - order[v,j] + n*x[v,i,j] <= n-1`.
- Truck load alone does not prevent subtours.

Service and load variables:
- Signed service: `s[v,i]`, integer, in [-C, C].
  - Positive means pickup; negative means dropoff.
  - This automatically forbids both picking up and dropping off at one stop.
- Link service to visits: `-C*visit <= s[v,i] <= C*visit`, where `visit = sum_j x[v,i,j]`.
- Load: `load[v,node]`, integer, in [0, C], defined for START, the stations and END.
- `load[v,START]` is the `start_load`. It is only required to lie in [0, C], so leave it as a decision variable. Fixing it to 0 is also valid but may give a worse objective.
- Load propagation along used arcs, with M = 2C:
  - `load[v,j] - load[v,i] - s_j <= M(1-x)`
  - `load[v,j] - load[v,i] - s_j >= -M(1-x)`
  - Here s_j = s[v,j] for a station j, and 0 when j = END.

Station inventory, with `net_i = sum_v s[v,i]`:
- Pickup cannot exceed stock: `net_i <= initial_bikes_i`.
- Dropoff cannot exceed free space: `net_i >= initial_bikes_i - station_capacity_i`.

Unmet target (never use Python `abs()` on solver expressions):
- `dev_i >= 0`
- `net_i - target_i <= dev_i`
- `target_i - net_i <= dev_i`

Objective: `sum dist*x + penalty_weight*sum dev`, minimized.

Solver parameters:
- `model.setParam("limits/time", 300)` (adjust to the size: few stations means fast).
- `limits/gap 0.0–0.01`.
- `model.hideOutput()`.
- Check `model.getNSols() > 0` before extracting.

**Extraction.**
- Follow successors from START until END, using arcs with `getVal > 0.5`. Fail if a node repeats.
- Round service values with `round()`.
- At each stop:
  - picked = `max(s,0)`, dropped = `max(-s,0)`.
  - Recompute load cumulatively from start_load: `load_after_stop = prev + picked - dropped`.
  - `end_load` = the load after the last stop.
- Recompute distance in Python from the route coordinates. Do not use the solver objective for this.
- Recompute the summary from the extracted numbers:
  - `unmet_i = abs(target - (pick - drop))`
  - `total_unmet_rebalancing_amount = sum(unmet_i)`
  - `unmet_rebalancing_penalty = penalty_weight * total_unmet_rebalancing_amount`
  - `objective = travel_distance_miles + unmet_rebalancing_penalty`

**Output format (`report.json`), numbers as floats:**
```json
{"summary":{"objective":..,"travel_distance_miles":..,"unmet_rebalancing_penalty":..,"total_unmet_rebalancing_amount":..},
 "vehicles":[{"vehicle_id":1,"start_load":0.0,"route":["depot_start",393,"depot_end"],
   "stops":[{"station_id":393,"bikes_picked_up":4.0,"bikes_dropped_off":0.0,"load_after_stop":4.0}],
   "end_load":4.0}],
 "stations":[{"station_id":393,"net_rebalancing_target":4.0,"total_bikes_picked_up":4.0,
   "total_bikes_dropped_off":0.0,"net_bike_change":4.0,"unmet_rebalancing_amount":0.0}]}
```
- Include one vehicle object per vehicle, with `vehicle_id` numbered 1..vehicle_count. Every vehicle visits at least one station.
- `route` lists the original integer station IDs between "depot_start" and "depot_end". Its middle entries must match the `stops` order exactly.
- Include one station object for every station in data.json, even unvisited ones (all zeros there).
- Station totals must equal the sums of the stop quantities across all vehicles.

**Validate (separate python one-liner or a function at the end of the script):**
- Routes start and end at the depot labels, with no repeated station within a vehicle.
- All loads, including start and end, are in [0, C], and no stop has both pickup and dropoff > 0.
- Final inventory `initial - pick + drop` is in [0, station_capacity].
- The summary arithmetic matches within 1e-6.
- The number of vehicle entries equals vehicle_count, and the number of station entries equals the number of stations.

Print only the summary and short per-vehicle routes, never the whole file.

**Plan.**
1. Inspect the keys and the first station; check pyscipopt is installed.
2. Write `/root/solve.py` (load data → distances → MIP → solve → extract → validate → dump).
3. Run it.
4. Print the summary and validation result.
5. If the solve hits the time limit with a large gap, raise the time limit or warm-start; never report an infeasible or unvalidated solution.
