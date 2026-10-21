# Associate phase picks with a candidate event catalog

Inputs in `/root/work`:

- `stations.csv` has the columns `station_id`, `x_km`, `y_km` and `elevation_m`. `x_km` and `y_km` are local Cartesian coordinates in km. `elevation_m` is the station elevation in meters above sea level.
- `events.csv` lists candidate earthquakes with the columns:
  - `event_id` (integer)
  - `time` (origin time, ISO format, UTC, no timezone)
  - `x_km`, `y_km`
  - `z_km` (hypocentre depth in km, positive downward)
- `picks.csv` has the columns `pick_id`, `station_id`, `phase` (`P` or `S`), `timestamp` (ISO arrival time with milliseconds) and `prob`.

Velocity model and geometry conventions:

- Use a uniform velocity model: `vp = 6.0 km/s` and `vs = vp/1.75`.
- The station vertical coordinate (depth, positive down) is `-elevation_m/1000` km.
- Travel time is the 3-D straight-line distance from hypocentre to station divided by the velocity of the pick's phase.

Task: for every pick, compute its residual against every candidate event:

`|observed arrival time - (event origin time + travel time for that pick's phase at that pick's station)|` in seconds.

- Assign the pick to the event with the smallest residual, but only if that residual is <= 1.0 s.
- Otherwise the pick is unassociated and gets `event_id = -1`.
- The `prob` column is not used.

Output: write `/root/work/assignments.csv`:

- Header: `pick_id,event_id`.
- Exactly one row for every pick in `picks.csv`, in any order.
- `event_id` is written as an integer (`-1` for unassociated picks).
