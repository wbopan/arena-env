# Civ6 Campus Site Ranking

A city has been founded. Rank every tile where it could build a Campus.

## Inputs
- `/root/work/map.json`: `{"width", "height", "tiles": [{"x", "y", "terrain", "feature", "resource"}]}`. Missing values are `null`.
- `/root/work/city.json`: `{"city_center": [x, y]}`.

## Conventions
- The hex grid uses odd-r offset coordinates: rows with `y % 2 == 1` are shifted right.
- The neighbours of (x,y) are:
  - for even y: (x+1,y), (x-1,y), (x-1,y-1), (x,y-1), (x-1,y+1), (x,y+1).
  - for odd y: (x+1,y), (x-1,y), (x,y-1), (x+1,y-1), (x,y+1), (x+1,y+1).
- Off-map neighbours are ignored.
- Hex distance is computed via cube coordinates: cx = x - (y - (y&1))/2, cz = y, cy = -cx-cz. The distance is half the sum of the absolute cube differences.
- A tile is a valid site if all of the following hold:
  - it is on the map;
  - its distance from the city center is 1 to 3;
  - its terrain is GRASS or PLAINS;
  - its feature is not GEOTHERMAL_FISSURE;
  - its resource is not strategic (IRON, COAL, HORSES, NITER, OIL, ALUMINUM, URANIUM) and not luxury (SILK, WINE, DIAMONDS).
- Evaluate each site alone. The only other district is the city center.
- WOODS and RAINFOREST on the city center tile do not count.
- Each half bonus is floored separately.

## Adjacency formulas
Counts are taken over the site's 6 neighbours. "districts" is 1 if the city center is adjacent, otherwise 0.
- campus = 2*GEOTHERMAL_FISSURE + 2*REEF + MOUNTAIN + floor(RAINFOREST/2) + floor(districts/2)
- holy_site = MOUNTAIN + floor(WOODS/2) + floor(districts/2)

MOUNTAIN is a terrain. REEF is a feature found on coast tiles.

## Output
Write `/root/work/campus_sites.csv` with the header `x,y,distance,campus,holy_site`.
- Include one row per valid site, with all values as integers.
- Sort by campus descending, then holy_site descending, then y ascending, then x ascending.
