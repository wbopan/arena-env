# Associate picks by inferred origin time

The inputs are `/root/work/stations.csv` and `/root/work/picks.csv`. Stations have local Cartesian coordinates `x_km` and `y_km`; all distances are in kilometers. Picks contain `station_id`, `phase`, `time_s`, and `prob`. Times are seconds after the start of the recording, not clock timestamps. The earthquake source is fixed at `(9, 0, 6)` km, where the third coordinate is depth. Stations are at depth zero. Use straight-line travel distances, P velocity 6 km/s, and S velocity 3 km/s.

Discard picks with `prob < 0.8`. For each remaining pick, subtract its phase travel time from `time_s` to obtain an inferred origin time. Sort these estimates and form clusters by joining consecutive estimates whenever their difference is at most 0.30 seconds. Keep a cluster only if it contains picks from at least three distinct stations and at least two P picks.

Write exactly `/root/work/events.csv`, with header `time_s,n_picks,n_stations`. Include one row per retained cluster, sorted by origin time. `time_s` is the arithmetic mean of its inferred origin times, rounded to three decimal places. The other fields are integer counts of picks and distinct stations, respectively. Do not include rejected picks in any count.
