# Audit a nightly bike-rebalancing plan

A dispatcher has proposed a rebalancing plan. Your job is to audit it, not to change it.

## Inputs

`/root/work/data.json` contains:

- `vehicle_capacity`
- `penalty_weight`
- `depot` with `latitude` and `longitude`
- `stations`: a list of objects, each with `id`, `latitude`, `longitude`, `initial_bikes`, `station_capacity` and `net_rebalancing_target`.

`/root/work/plan.json` contains `vehicles`. Each vehicle has `vehicle_id`, `start_load` and an ordered list `stops`. Each stop has `station_id`, `bikes_picked_up` and `bikes_dropped_off`.

## Rules

**Route.** Each vehicle drives from the depot, through its stops in order, and back to the depot.

**Distance.** Use great-circle miles on a sphere of radius 3960.0. Coordinates are in degrees.

**Vehicle loads.**

- The load sequence is `start_load`, followed by each `load_after_stop`.
- `load_after_stop = previous load + bikes_picked_up - bikes_dropped_off`.
- `capacity_ok` is true when every load in the sequence is between 0 and `vehicle_capacity`, inclusive.

**Stations.**

- Per-station totals are summed over all vehicles. A station that no vehicle visits has totals of 0.
- `final_inventory = initial_bikes - total_bikes_picked_up + total_bikes_dropped_off`.
- `inventory_ok` is true when `0 <= final_inventory <= station_capacity`.
- `unmet_rebalancing_amount = abs(net_rebalancing_target - (total_bikes_picked_up - total_bikes_dropped_off))`.

**Summary.**

- `unmet_rebalancing_penalty = penalty_weight * total_unmet_rebalancing_amount`.
- `objective = travel_distance_miles + unmet_rebalancing_penalty`.
- `all_feasible` is true only when every `capacity_ok` and every `inventory_ok` is true.

## Output

Write `/root/work/audit.json` with three keys:

- `vehicles`: one object per vehicle, in `plan.json` order, with `vehicle_id`, `distance_miles`, `min_load`, `max_load`, `end_load` and `capacity_ok`.
- `stations`: one object per station, in `data.json` order, with `station_id`, `total_bikes_picked_up`, `total_bikes_dropped_off`, `final_inventory`, `inventory_ok` and `unmet_rebalancing_amount`.
- `summary`: `travel_distance_miles`, `total_unmet_rebalancing_amount`, `unmet_rebalancing_penalty`, `objective` and `all_feasible`.

Formatting:

- Round mile and penalty values to 4 decimals.
- Write counts as integers.
- Write flags as JSON booleans.
