# Civ6 District Adjacency Audit

Compute the adjacency bonuses of several fixed district layouts.

## Inputs
- `/root/work/map.json`: `{"width", "height", "tiles": [{"x", "y", "terrain", "feature", "resource", "improvement"}]}`. Missing values are `null`.
- `/root/work/layouts.json`: a list of layouts. Each has an `id`, a `city_center` `[x, y]` and `districts` mapping `CAMPUS`, `HOLY_SITE` and `INDUSTRIAL_ZONE` to `[x, y]`. All placements are valid. Each layout is evaluated independently.

## Conventions
- The hex grid uses odd-r offset coordinates: rows with `y % 2 == 1` are shifted right.
- The neighbours of (x,y) are:
  - for even y: (x+1,y), (x-1,y), (x-1,y-1), (x,y-1), (x-1,y+1), (x,y+1).
  - for odd y: (x+1,y), (x-1,y), (x,y-1), (x+1,y-1), (x,y+1), (x+1,y+1).
- Off-map neighbours are ignored.
- The occupied tiles of a layout are its city center plus its 3 districts. On occupied tiles, `WOODS` and `RAINFOREST` features and all improvements are destroyed, so they are not counted.
- "districts" means the number of adjacent occupied tiles. The city center counts as a district.
- Strategic resources are IRON, COAL, HORSES, NITER, OIL, ALUMINUM and URANIUM.
- Each half bonus is floored separately.

## Adjacency rules
Counts are taken over the 6 neighbours of the district.
- CAMPUS = 2*GEOTHERMAL_FISSURE + 2*REEF + MOUNTAIN + floor(RAINFOREST/2) + floor(districts/2)
- HOLY_SITE = MOUNTAIN + floor(WOODS/2) + floor(districts/2)
- INDUSTRIAL_ZONE = QUARRY + strategic + floor(MINE/2) + floor(LUMBER_MILL/2) + floor(districts/2)

MOUNTAIN is a terrain. QUARRY, MINE and LUMBER_MILL are improvements.

## Output
Write `/root/work/adjacency.json`:
```json
{"layouts": [{"id": "L1", "bonuses": {"CAMPUS": 0, "HOLY_SITE": 0, "INDUSTRIAL_ZONE": 0}, "total": 0}], "grand_total": 0}
```
- Keep the layouts in input order.
- All values are integers.
- `total` is the sum of the layout's bonuses.
- `grand_total` is the sum of all totals.
