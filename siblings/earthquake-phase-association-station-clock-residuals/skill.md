## Reference notes

Use Python’s standard-library `csv`, `math`, `statistics`, and `json`. **Do not use GaMMA association**: the events and P picks are already supplied, and its clustering API does not implement the specified catalog-residual matching.

```python
from pathlib import Path
import csv, json, math
from statistics import median

base = Path("/root/work")
with (base / "stations.csv").open(newline="") as f:
    stations = list(csv.DictReader(f))
# Read events.csv and picks.csv the same way.
```

`csv.DictReader` returns strings: preserve IDs as strings; convert coordinate, time, depth, and probability fields with `float()` when calculating. Check the CSV headers before writing the script. The `channel` field does not enter the travel-time calculation or the station–event deduplication key.

For a source at `(event.x_km, event.y_km, event.depth_km)` and a depth-zero station at `(station.x_km, station.y_km)`:

```python
distance_km = math.sqrt(
    (station_x - source_x)**2
    + (station_y - source_y)**2
    + source_depth**2
)
travel_s = distance_km / 6.0
residual_s = pick_time_s - origin_time_s - travel_s
```

Workflow:

1. For **each pick**, calculate a residual for **every** catalog event. Select with `min(candidates, key=lambda item: (abs(item.residual), item.event_id))`; this resolves exact absolute-residual ties lexicographically by event ID.
2. Reject picks with `prob < 0.8` or selected `abs(residual_s) > 2`. Boundary values are retained.
3. Among accepted picks sharing `(station_id, event_id)`, retain highest probability, then earliest observed `time_s` on a probability tie. Retain that pick’s residual; do not average channels.
4. Group retained residuals by station. `statistics.median(values)` gives the offset; `len(values)` gives the count. Round the median with `round(offset, 3)`.
5. Build the output from **all rows in `stations.csv`**, including stations without retained picks (`offset_s: None`, `count: 0`). Sort by string `station_id`, then write the JSON array to `/root/work/clock_offsets.json` using `json.dump(...)`. Python `None` serializes as JSON `null`.

Keep calculations at full precision until the final rounding; do not round residuals before matching, filtering, or taking medians.
