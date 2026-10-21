1. Inspect data.json keys and one station record with a python one-liner, and confirm pyscipopt imports.
2. Build a PySCIPOpt VRP:
   - per-vehicle binary arcs `depot_start → stations → depot_end` (no direct depot arc), with each route used exactly once, flow conservation, and at most one visit per vehicle;
   - MTZ subtour elimination;
   - signed integer service in [-C, C] linked to visits, and big-M load propagation with loads in [0, C];
   - station inventory bounds, plus abs-deviation slack times penalty_weight in the objective.
3. Extract the routes, recompute distance (great circle, R = 3960) and all totals in Python, and write `/root/report.json` with floats and original station IDs, covering all vehicles and all stations.
4. Run an independent validator on the loads, inventories, routes and summary arithmetic before finishing.
