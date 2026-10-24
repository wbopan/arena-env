## Reference notes

Use Python’s standard-library `json` and `csv`; this is an audit of the supplied plan, not a routing problem to solve. Read `t_matrix.csv` with `csv.reader` and convert every field to `int`. It has **no header**: `matrix[from_node][to_node]` gives travel minutes.

Build a lookup from each pickup/dropoff service node to its trip, event type, and corresponding time window. Keep request IDs and trip IDs in their input types; sort the output ID lists without converting IDs to strings.

For each route, traverse `node_sequence` **in its given order**, starting at `config["depot_node"]`, `route["start_time"]`, and load zero:

```python
arrival = departure + matrix[previous_node][node]
service_start = max(arrival, window[0])
total_wait += service_start - arrival
# Check service_start <= window[1].
# Record pickup/dropoff service starts; adjust load by +load / -load.
max_load = max(max_load, onboard)
departure = service_start + config["service_time"]
previous_node = node
```

The initial `departure` is `start_time`; **do not** add service time at the depot. For a nonempty route, `end_time = departure + matrix[previous_node][depot_node]`. For an empty route, `end_time = start_time`, with zero wait and max load.

Independently check each route’s pairing (both events present on that route, pickup earlier), window highs, capacity, shift duration (`end_time - start_time`), and each trip’s ride time (`dropoff_service_start - pickup_service_start`). Waiting to reach a window low is permitted. A trip is served only on a feasible route; a request is served only when **all** its trips are served. `served_trips` contains only trips belonging to those fully served requests.

Write JSON with route summaries in plan order and the two ID lists sorted. A short workflow: inspect the input shapes, write one audit script, run it, then open `report.json` to check its structure and integer-valued metrics.
