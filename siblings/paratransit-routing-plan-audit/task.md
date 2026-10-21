# Audit a paratransit day plan

Inputs in `/root/work`:
- `requests.json`: a list of requests. Each request has `request_id` and `trips`. Each trip has `trip_id`, `pickup_node`, `dropoff_node`, `load`, `pickup_tw` and `dropoff_tw`. Windows are `[low, high]` in minutes.
- `t_matrix.csv`: integer travel minutes with no header. The row is the from-node and the column is the to-node.
- `config.json`: `capacity`, `service_time`, `shift_duration`, `max_ride_time`, `depot_node`.
- `plan.json`: `routes`, each with `vehicle_id`, `start_time` and `node_sequence`. The sequence lists service nodes only; the depot is excluded.

Simulate each route:
- The vehicle leaves the depot at `start_time`.
- arrival = previous departure + travel.
- service start = max(arrival, window low).
- wait = service start - arrival.
- departure = service start + service_time.
- end_time = last departure + travel back to the depot. If the route is empty, end_time = start_time.
- Onboard load starts at 0. It rises by the trip load at the pickup and falls by it at the dropoff.
- `max_load` is the largest onboard load after any stop (0 if the route is empty).

A route is feasible only if all of these hold:
- Every trip that touches the route has both its pickup and its dropoff on it, with the pickup first.
- No service start exceeds its window high.
- Onboard load never exceeds capacity.
- end_time - start_time <= shift_duration.
- For every trip, dropoff service start - pickup service start <= max_ride_time.

A trip is served if it lies on a feasible route. A request is served only if all of its trips are served (all-or-none).

Write `/root/work/report.json` in this form:
`{"routes": [{"vehicle_id": str, "feasible": bool, "end_time": int, "max_load": int, "total_wait": int}, ...], "served_trips": [...], "served_requests": [...]}`

- List the routes in plan order.
- `total_wait` is the sum of waits on the route.
- `served_trips` contains the sorted trip_ids belonging to served requests only.
- `served_requests` contains the sorted request_ids.
- All times are integer minutes.
