## Reference notes

Use Python’s standard `json` and `math`; no geospatial library is needed for the specified projection. In a GeoJSON Polygon, `feature["geometry"]["coordinates"][0]` is its **exterior ring**, with coordinates ordered `[longitude, latitude]`. Select the feature by `feature["properties"]["Code"] == "PA"`.

Strict containment can be checked with a ray-crossing test, but check for a point **on any edge first** and exclude it. A ring may repeat its first vertex at the end; `zip(ring, ring[1:] + ring[:1])` visits every edge (with a harmless zero-length edge if it is already closed).

Project both the earthquake and **every ring vertex** before measuring distance. Use the task’s formula directly, without longitude wrapping:

```python
from math import pi

SCALE = 6378137 * pi / 180
def project(lonlat):
    lon, lat = lonlat
    return (SCALE * lon, SCALE * lat)
```

Distance is to each **whole projected edge**, not just its endpoints. For point `p` and segment endpoints `a, b`:

```python
dx, dy = b[0] - a[0], b[1] - a[1]
length2 = dx*dx + dy*dy
t = 0 if length2 == 0 else max(
    0, min(1, ((p[0]-a[0])*dx + (p[1]-a[1])*dy) / length2)
)
distance_m = math.hypot(p[0]-(a[0]+t*dx), p[1]-(a[1]+t*dy))
```

Take the minimum over **PA’s exterior-ring edges only**. Do not use Haversine distance, distances in degrees, or another plate’s boundary.

Short workflow: read the GeoJSON FeatureCollection and earthquake JSON array; select PA’s ring; exclude edge points and retain strictly interior earthquakes; compute each retained point’s minimum projected point-to-segment distance in metres; sort by `(-distance_m, id)` **before rounding**; take three; convert metres to kilometres and round to two decimals. Write one JSON array whose objects contain exactly `id`, `plate_code`, and `clearance_km`.
