## Reference notes

Use Python’s standard-library `csv`, `json`, and `math`; no geospatial package is needed. **Follow the task’s projection exactly**, rather than substituting EPSG:4087 or a great-circle distance:

```python
import math

R = 6371.0
def project(lon, lat):
    return (R * math.radians(float(lon)),
            R * math.radians(float(lat)))

def point_segment_distance(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length2 = dx*dx + dy*dy
    t = 0.0 if length2 == 0 else max(0.0, min(1.0,
        ((p[0]-a[0])*dx + (p[1]-a[1])*dy) / length2))
    return math.hypot(p[0] - (a[0] + t*dx),
                      p[1] - (a[1] + t*dy))
```

- Read the GeoJSON FeatureCollection with `json.load`. Each feature’s `geometry.coordinates` is a sequence of **`[longitude, latitude]`** vertices. Project vertices once; a feature’s distance is the minimum over its consecutive vertex pairs. Measure to **segments**, not just vertices. Do not combine features: the nearest *feature* determines its `properties["Type"]`.
- Read the CSV with `csv.DictReader`; numeric fields are strings, so convert `mag`, `latitude`, and `longitude` to `float`. Filter `mag >= 4.5` before counting or associating.
- Find the minimum distance across all features first. Associate its type only when `distance <= 200` (inclusive); otherwise increment `unassociated_count`. Distances from `project()` are already in km. Do not wrap longitudes or apply latitude-dependent scaling.
- For each of the three required types, accumulate associated distances and magnitudes. Set `mean_distance_km` to `round(sum(distances) / count, 2)` and `max_magnitude` to the maximum magnitude; use Python `None` for both when `count == 0` (`json.dump` writes it as `null`).

A short workflow: inspect the GeoJSON feature/coordinate shape and CSV header cheaply; write one script that reads, projects, associates, aggregates, and writes `/root/work/boundary_summary.json`; run it, then reopen the JSON to check its structure and counts.
