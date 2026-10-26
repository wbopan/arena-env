# Locate earthquake footpoints on plate boundaries

`/root/work/boundaries.geojson` is a WGS84 GeoJSON FeatureCollection of LineString plate boundaries. Each feature has a unique `BoundaryID`; a LineString may contain several straight segments. `/root/work/earthquakes.json` is a JSON array of objects with `id`, `longitude`, and `latitude`. Coordinates are longitude first, in degrees.

For every earthquake, find the closest point on any boundary segment, allowing the closest point to lie between vertices. Compute all distances in the EPSG:4087 metric plane, using `x = 6378137 × longitude × π/180` and `y = 6378137 × latitude × π/180`. The chosen boundary is the one containing the globally closest point. If distances tie exactly, choose the lexicographically smaller `BoundaryID`.

Write `/root/work/footpoints.csv`, with a header and one row per earthquake, sorted by ascending earthquake `id`. Its columns, in this exact order, are `id,boundary_id,foot_lon,foot_lat,distance_km,station_km`. `foot_lon` and `foot_lat` are the closest point's WGS84 coordinates. `station_km` is distance along the chosen LineString from its first vertex to that point, not distance from the earthquake. Round the four numeric output fields to three decimal places. No earthquake should be omitted.
