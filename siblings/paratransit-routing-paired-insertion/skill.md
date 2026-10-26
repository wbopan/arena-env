## Reference notes

Use Python standard-library `json` and `csv`; this fixed-order, single-pair insertion is small enough to enumerate directly. No routing solver is needed.

- Inspect the JSON structure before choosing field names. Read the travel matrix with `csv.reader`, **not** `DictReader`: it has no header. Its rows and columns both follow `DEP,P0,D0,P1,D1,P2,D2`; map node labels to matrix positions explicitly. Convert travel times and all minute/load fields to integers.
- Preserve the four existing service stops in their original relative order. For each candidate, place the new pickup at a final-list position `p` and its dropoff at a position `d > p`. Positions exclude the starting and ending depots.
- Simulate each candidate from `start_min` at `DEP`. At each service stop:
  ```python
  arrival = previous_start + previous_duration + travel[previous_node][node]
  service_start = max(arrival, window_low)
  # infeasible if service_start > window_high
  ```
  Windows apply to **service starts** and include both endpoints. The first depot’s service duration is zero. After every pickup add that trip’s passenger load; after every dropoff subtract it. Reject a route if load leaves `[0, capacity]`. For the final depot, propagate time using the last stop’s duration and its travel-to-`DEP` time; reject arrival after `end_limit_min`.
- Compute route travel as the sum of matrix entries for every consecutive leg, including both depot legs; waiting and service durations do **not** contribute. Compute the original route’s travel the same way. Compare feasible candidates by `(candidate_travel - original_travel, p, d)`.
- Write exactly the four requested keys with `json.dump`. `service_starts_min` contains service-start times for service stops only, in final route order; do not include depot times or round values.

A compact workflow is: load and inspect the two JSON objects and matrix; normalize stop/node, trip, window, duration, and load lookups; write one route-simulation function; enumerate ordered insertion positions; retain the minimum comparison tuple; write the selected candidate’s indices, added travel, and simulated service starts.
