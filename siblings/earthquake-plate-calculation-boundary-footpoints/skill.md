## Reference notes

Use Python standard-library `json` and `csv`; no geospatial package is needed because the task specifies the EPSG:4087 transform exactly. GeoJSON coordinates are `[longitude, latitude]`. Read `features[*].properties["BoundaryID"]` and `features[*].geometry["coordinates"]`; each consecutive coordinate pair is a segment. Keep segments grouped by feature so their `BoundaryID` and position along the original LineString are preserved. **Do not union the lines:** that loses boundary identity and station origin.

```python
import json, csv, math

R = 6378137.0
SCALE = R * math.pi / 180.0

def project(lon, lat):
    return (SCALE * lon, SCALE * lat)

def unproject(x, y):
    return (x / SCALE, y / SCALE)
```

For earthquake point \(P\) and projected segment endpoints \(A,B\), let \(V=B-A\). The closest point on that **segment**, including its endpoints, is:

```python
length2 = vx*vx + vy*vy
t = max(0.0, min(1.0, ((px-ax)*vx + (py-ay)*vy) / length2)) if length2 else 0.0
fx, fy = ax + t*vx, ay + t*vy
distance_m = math.hypot(px-fx, py-fy)
```

A zero-length segment has its foot at `A`. For a segment starting `distance_before_m` metres from the LineString’s first vertex, `station_m = distance_before_m + t * math.sqrt(length2)`. Accumulate each segment’s **projected planar length** in vertex order.

Compare candidates using unrounded distances across **all** features and segments. On an exact distance tie, select the lexicographically smaller `BoundaryID`; do not round before comparing. Convert the selected foot back with `unproject`, and convert distance and station from metres to kilometres.

Write CSV with `csv.writer`, header exactly `id,boundary_id,foot_lon,foot_lat,distance_km,station_km`, one row per earthquake sorted by ascending `id`. Format the four numeric output fields with `f"{value:.3f}"`. A short workflow: inspect the JSON structures, write and run one script, then check the header, row count, ordering, and representative output rows.
