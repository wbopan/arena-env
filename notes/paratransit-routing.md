**Read the spec first.** `/root/model-and-data.md` defines the data files, the feasibility rules and the exact report schema. Read it in chunks to save tokens: `wc -l /root/model-and-data.md`, then `sed -n '1,80p'` and so on. Write down these items:

- Input file paths and formats.
- Units: minutes, and whether times are seconds or minutes from midnight.
- How the travel matrix is indexed (external node IDs and depot IDs).
- Invalid-arc sentinels (negative, null or huge values).
- Service-time convention.
- Pickup and dropoff time-window formulas.
- Maximum ride time and maximum wait, if any.
- Vehicle capacity.
- Shift duration and allowed shift starts (for example top-of-hour inside an operating window).
- Whether trips are grouped (one passenger or request set must be fully served or fully rejected).
- The objective (maximize served trips, then tie-breaks).
- The exact JSON keys for `/root/report.json`.

Then inspect the data cheaply:

- `ls -la /root`
- `head -c 600 file`
- For JSON: `python3 -c "import json;d=json.load(open(F));print(type(d), list(d)[:20] if isinstance(d,dict) else len(d))"`
- For CSV: `head -3 f.csv; wc -l f.csv`
- Check that matrix shape equals node count, and check vehicle count.
- Confirm OR-Tools is available: `python3 -c "import ortools;print(ortools.__version__)"`. If missing, run `pip install ortools`.

**Model (OR-Tools `pywrapcp.RoutingModel`).**

1. **Integers only.** Convert travel times, service times, windows and demands to int. Map invalid arcs to a large but non-overflowing sentinel (for example `10**6`). Also forbid them by never letting a final route use them; reject any route that does.
2. **Nodes and depots.**
   - Create one pickup node and one dropoff node per trip.
   - Pickup demand is +load (usually 1 or the passenger count). Dropoff demand is the negative of that.
   - Clone depots: job nodes first, then one start node per vehicle, then one end node per vehicle.
   - Use `matrix[start_v][end_v]=0`. Set job→end to travel to the end depot and start→job to travel from the start depot.
   - Depots have 0 demand and 0 service time.
   - Keep a map from internal node to (trip_id, kind, external location).
3. **Time dimension.**
   - Transit(i→j) = travel[i][j] + service[i], with service charged at the departing node. `CumulVar` is then the arrival or service start, and departure = cumul + service.
   - Register with `routing.RegisterTransitMatrix(time_matrix)`, built over `manager.IndexToNode(index)` for all indices.
   - Use `routing.AddDimension(cb, slack=horizon, horizon, False, "Time")`. `fix_start_cumul_to_zero` must be False because shifts vary.
4. **Time windows.** Apply exactly the formulas in the spec with `time_dim.CumulVar(idx).SetRange(lo, hi)`. Do not shift windows by service time unless the spec says to. A typical derived window is pickup window = dropoff window minus direct travel.
5. **Pairs.** For each trip:
   ```python
   routing.AddPickupAndDelivery(p, d)
   solver.Add(routing.VehicleVar(p) == routing.VehicleVar(d))
   solver.Add(time_dim.CumulVar(p) <= time_dim.CumulVar(d))
   ```
   For a maximum ride time, add `solver.Add(time_dim.CumulVar(d) - (time_dim.CumulVar(p) + service_p) <= max_ride)`. Use the spec's exact definition of ride time.
6. **Capacity.**
   ```python
   cb = routing.RegisterUnaryTransitVector(demands)
   routing.AddDimensionWithVehicleCapacity(cb, 0, caps, True, "Capacity")
   ```
7. **Shifts.**
   - Set start and end cumuls to the operating window with `SetRange`.
   - Restrict the start cumul to the allowed shift starts with `time_dim.CumulVar(routing.Start(v)).SetValues(shift_starts)`. Example menu: `[m for m in range(0,1441,60) if lo<=m<=hi-shift_len]`.
   - Cap shift length with `time_dim.SetSpanUpperBoundForVehicle(shift_len, v)`.
   - Add `routing.AddVariableMinimizedByFinalizer` on the start cumul and `AddVariableMaximizedByFinalizer` on the end cumul.
   - If the spec measures shift length from shift start to return, the span bound matches that.
8. **Optional service and objective.**
   - Independent trips: `AddDisjunction([p], BIG)`.
   - Connected sets (all-or-none groups):
     - Put all of the group's pickups in one disjunction: `routing.AddDisjunction(pickups, len(g)*BIG, len(g))`.
     - Make each dropoff optional at zero penalty: `routing.AddDisjunction([d], 0)`.
     - Do not use hard equality constraints across the group.
   - Choose BIG (for example `10**7`) so that serving one more trip dominates any travel cost.
   - Set the secondary arc cost to travel time via `SetArcCostEvaluatorOfAllVehicles(cost_cb)`. This gives the search a gradient.
9. **Search.**
   - `first_solution_strategy=AUTOMATIC`
   - `local_search_metaheuristic=GENERIC_TABU_SEARCH`
   - `time_limit.seconds` set to the spec's limit if one is given. Otherwise use about 120–300 s, well under the command timeout.
   - Run with `python3 -u` and print flushed progress before and after the solve.
10. **Extraction.** Follow `solution.Value(routing.NextVar(i))` from `routing.Start(v)` until `routing.IsEnd`.
11. **Postprocess and audit from scratch** in plain Python, without reusing solver cumuls:
    - For grouped trips, keep only groups whose every pickup and dropoff is on a route, with each pair on the same vehicle. Drop the stops of partial groups and keep the remaining order.
    - Recompute along each route, starting at the chosen shift start: arrival = previous departure + travel, service start = max(arrival, window lo), check ≤ window hi, departure = start + service.
    - Also check: running load stays between 0 and capacity and ends at 0; ride and wait limits hold; no invalid arcs are used; the return to the depot is within the shift length and operating window; pickup comes before dropoff.
    - If a route fails, drop the offending trip or group and re-audit.
    - Count served trips only after the audit passes.
12. **Write `/root/report.json`** exactly in the spec's schema: key names, ID types (string or int, external IDs and depot IDs rather than internal clones), and stop representation. Include shift start per vehicle, include empty or unused vehicles only if the spec requires it, and use the spec's time units. If the spec says the verifier recomputes timings, write only the requested fields.

**Pitfalls**

- Confusing internal routing indices with node IDs. Always convert with `manager.NodeToIndex` and `manager.IndexToNode`.
- Float or NaN values in the matrices.
- A horizon that is too small for waiting.
- Counting partial groups as served.
- Forgetting the depot return within the shift.
- The load cumul in OR-Tools is the load before the node, so audit load from the sequence.
- Printing whole files or matrices.

**Plan**

1. Read the spec in chunks.
2. Peek at the data shapes.
3. Write `/root/solve.py`: load, build, solve, audit, then write JSON and print a summary of served/total trips, vehicles used and violations.
4. Run it with `timeout` and `python3 -u`.
5. Validate the output: `python3 -c "import json;r=json.load(open('/root/report.json'));print(list(r)[:10])"`. Compare its keys and types against the spec, and spot-check one route.
6. If time remains and there are no violations, optionally rerun with a longer limit. Keep the better audited result.
