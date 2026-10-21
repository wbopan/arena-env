# Sequence one rebalancing truck through every station

One rebalancing truck must service every station listed in `/root/work/truck.json` tonight.

## Input

`/root/work/truck.json` contains:

- `vehicle_capacity`
- `start_load`: the number of bikes on the truck when it leaves the depot.
- `depot` with `latitude` and `longitude`.
- `stations`: a list of objects, each with `id`, `latitude`, `longitude` and `net_rebalancing_target`.

The sign of `net_rebalancing_target` sets the operation:

- Positive: the truck must pick up exactly that many bikes at the station.
- Negative: the truck must drop off exactly that many bikes there.

## Rules

- The truck leaves the depot, visits every station exactly once and returns to the depot.
- At each stop it performs exactly the target operation. A stop is never both a pick-up and a drop-off.
- `load_after_stop = previous load + bikes_picked_up - bikes_dropped_off`. The previous load for the first stop is `start_load`.
- Every `load_after_stop` must be between 0 and `vehicle_capacity`, inclusive.
- Distances are great-circle miles on a sphere of radius 3960.0, between coordinates given in degrees.

## Goal

Find the visiting order that satisfies every rule above and minimizes the total travel distance. The tour is depot -> first station -> ... -> last station -> depot.

## Output

Write `/root/work/route.csv` as a comma-separated file.

- Header line, exactly: `position,station_id,bikes_picked_up,bikes_dropped_off,load_after_stop`
- Then one row per station, in visiting order.
- `position` starts at 1.
- `station_id` is the station's `id` from the input.
- All values are non-negative integers.
- Do not add extra rows or columns.
