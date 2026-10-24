### Reference notes

Use Python’s standard-library `json`, `csv`, and `math`; GeoJSON can be read without geospatial packages. Each plate’s `geometry.coordinates[0]` is its exterior ring. An earthquake’s `geometry.coordinates[:2]` is `(longitude, latitude)`; ignore the depth coordinate. Read `Code` and `id` from `properties`.

- Determine containment against each plate ring using a point-in-polygon method such as ray casting. Treat a point **on an edge** as outside if “inside” is interpreted strictly. The plates do not overlap, so stop at the first containing plate.
- Use **only that plate’s exterior ring** for distance—not a union of plate boundaries. Do not use haversine distance, degree-based distance, latitude-dependent scaling, or the earthquake’s depth.
- Project every point and ring vertex with the specified formula:

```python
from math import radians, hypot

R = 6371.0
def project(lon, lat):
    return R * radians(lon), R * radians(lat)
```

For projected point `P` and consecutive projected vertices `A`, `B`, the nearest point on the **segment** is at
`t = clamp(dot(P−A, B−A) / |B−A|², 0, 1)`. Distance is `hypot(P.x − (A.x + t*(B.x−A.x)), P.y − (A.y + t*(B.y−A.y)))`. If `A == B`, use the distance to `A`. Take the minimum over all ring edges. Check whether the GeoJSON ring repeats its first vertex; if not, include the closing edge from last to first. Keep longitudes as supplied: the stated projection does not call for ±360° wrapping.

Round distances to two decimals **before sorting**, so equal displayed distances are tied by ascending `id`. Write with `csv.writer`, header `["id", "plate_code", "distance_km"]`, and no index. A compact workflow is: inspect feature counts and coordinate shapes, load both JSON files, prepare each plate’s ring and projected edges once, process each earthquake, sort retained rows by `(-rounded_distance, id)`, then write and briefly inspect the CSV.
