1. Read `/root/model-and-data.md` in chunks with `sed -n`, noting windows, ride/wait/shift/capacity rules, groups and the exact report schema. Peek at the data with `head` and short python one-liners.
2. Write one `python3 -u` script using OR-Tools RoutingModel:
   - Cloned depots; Time dimension with travel plus service at the departing node.
   - Pickup-delivery pairs with same-vehicle and precedence constraints, plus capacity.
   - Shift starts via `SetValues` and `SetSpanUpperBoundForVehicle`.
   - Large-penalty disjunctions (grouped pickups, zero-penalty dropoffs); `AUTOMATIC` with `GENERIC_TABU_SEARCH` under a time limit.
3. Independently re-audit every route, removing partial groups and violators, then write `/root/report.json` in the exact schema.
4. Verify the JSON keys and types and the served count.
