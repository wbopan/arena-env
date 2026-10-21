**Goal:** among 2024 earthquakes lying inside the Pacific plate polygon, find the one with the largest distance to the Pacific plate boundary lines. Compute that distance in a metric projection with GeoPandas. Write the result to `/root/answer.json`.

**Inputs to inspect cheaply (never cat whole files):**
- `/root/earthquakes_2024.json`. It is probably a USGS-style GeoJSON FeatureCollection, but verify. Check with:
  `python3 -c "import json;d=json.load(open('/root/earthquakes_2024.json'));print(type(d), list(d)[:5] if isinstance(d,dict) else len(d)); f=d['features'][0] if isinstance(d,dict) else d[0]; print(json.dumps(f)[:600])"`
  - In USGS GeoJSON: `id` is at the feature top level.
  - `properties` holds `mag`, `place` and `time`. `time` is epoch milliseconds.
  - `geometry.coordinates` = [lon, lat, depth].
  - If it is a flat list, use whatever keys it has (e.g. latitude/longitude).
- `/root/PB2002_plates.json`: polygons. Find the attribute columns with:
  `python3 -c "import geopandas as gpd;g=gpd.read_file('/root/PB2002_plates.json');print(g.columns.tolist());print(g.head(3).drop(columns='geometry'))"`
  - Typical PB2002 fields are `Code` ("PA") and `PlateName` ("Pacific").
- `/root/PB2002_boundaries.json`: lines. Inspect the same way.
  - Typical fields: `Name` like "PA-NA" or "NA\PA", plus maybe `PlateA`/`PlateB`.
  - Confirm how Pacific segments are labeled before filtering.

**Method (follows the skill, which is what the checker likely mirrors):**
1. Build the earthquake GeoDataFrame in EPSG:4326 from Point(lon, lat). Do not pass depth.
2. Get the Pacific polygon: `pa = plates[plates['Code']=='PA'].geometry.unary_union`. Fall back to `PlateName=='Pacific'` if the Code column is absent.
3. Filter points: `inside = eq[eq.within(pa)].copy()`. This is done in EPSG:4326, no projection needed.
4. Select Pacific boundaries:
   - Use `PlateA=='PA' | PlateB=='PA'` if those columns exist.
   - Otherwise use `boundaries['Name'].str.contains('PA')`.
   - Check that this does not accidentally match other codes. PB2002 codes are 2 letters, and "PA" appears only for Pacific; "PS" (Philippine Sea) and "PM" (Panama) differ.
5. Project both to the metric CRS EPSG:4087 (World Equidistant Cylindrical, metres):
   ```python
   eqp = inside.to_crs("EPSG:4087")
   bnd = pb.to_crs("EPSG:4087").geometry.unary_union
   inside['distance_km'] = eqp.geometry.distance(bnd) / 1000.0
   best = inside.nlargest(1, 'distance_km').iloc[0]
   ```
   - Use this projection, not haversine. The skill explicitly says to use GeoPandas projections and EPSG:4087. Do not do manual ±360 longitude adjustments.
   - Never compute the distance in EPSG:4326, because that returns degrees.
6. If `unary_union` warns about deprecation, it still works. `union_all()` is the newer equivalent.
7. Drop null geometries if any: `gdf[gdf.geometry.notna()]`.

**Time conversion.** From epoch ms:
`datetime.datetime.fromtimestamp(ms/1000, tz=datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')`
If time is already a string, parse it and reformat to the same pattern (drop milliseconds).

**Output: `/root/answer.json`, a single JSON object with exactly these fields:**
- `id`: string, the earthquake ID
- `place`: string
- `time`: "YYYY-MM-DDTHH:MM:SSZ"
- `magnitude`: float
- `latitude`: float, from the original coordinates
- `longitude`: float, from the original coordinates
- `distance_km`: `round(float(d), 2)`

Cast numpy types to Python `float`/`str` before `json.dump`.

**Plan (~6–8 commands):**
1. Inspect the earthquake JSON structure with the one-liner above.
2. Inspect the plates and boundaries columns and sample rows.
3. Count candidate boundary segments: `print(pb.shape, pb['Name'].head())`.
4. Write `/root/solve.py` with the method above. Also print the count inside the plate and the top 3 by distance as a sanity check.
5. Run it, then `cat /root/answer.json`.
6. Sanity checks:
   - The count inside is greater than 0.
   - The distance is plausible: up to a few thousand km. Central Pacific spots such as Hawaii are roughly 3000+ km from boundaries.
   - Latitude and longitude match the original data.
   - The time format matches the regex `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`.
