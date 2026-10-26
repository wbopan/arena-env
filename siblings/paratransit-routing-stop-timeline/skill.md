## Reference notes

- This is **timeline reconstruction for a fixed route**, not route optimization; use Python standard-library `json` and `csv`. No OR-Tools model is needed.
- Inspect the JSON structure and a few records before choosing keys: `requests.json` supplies the trip-to-pickup/dropoff mapping, loads, service durations, and service-start windows; `route.json` supplies `start_min` and `node_sequence`. Preserve request order when building the matrix index: `DEP, P0, D0, P1, D1, ...`. Do **not** index the matrix by position in the route.
- `t_matrix.csv` has **no header**. Read every field as an integer, for example:
  ```python
  with open("/root/work/t_matrix.csv", newline="") as f:
      travel = [[int(x) for x in row] for row in csv.reader(f)]
  ```
  The first and final `DEP` occurrences both use matrix index 0. Check that the matrix is square with `1 + 2 * len(requests)` rows, adapting `requests` to the inspected JSON structure.

For each stop **after the first depot**, use the preceding stop’s departure:
```text
arrival = previous_departure + travel[index[previous_node]][index[node]]
```
At a service stop with inclusive service-start window `[low, high]`:
```text
service_start = max(arrival, low)
wait = service_start - arrival
departure = service_start + service_duration
load_after = previous_load + load   # pickup
load_after = previous_load - load   # dropoff
```
Check `service_start <= high` and `0 <= load_after <= 4`. Windows constrain **service start**, not arrival or departure.

For the first depot, set arrival, start, and departure to the route’s `start_min`; waiting and load are zero. At the final depot, arrival equals the propagated travel arrival; start and departure equal arrival, waiting is zero, and load is unchanged. Keep a separate output row for each depot occurrence.

Write with `csv.writer` and `newline=""`, using exactly:
```python
["node", "arrival_min", "start_min", "depart_min", "wait_min", "load_after"]
```
Keep all values integer; check the row count matches `node_sequence` and the final load is zero.
