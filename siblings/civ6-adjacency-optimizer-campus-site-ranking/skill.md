## Reference notes

Use Python’s standard-library `json` and `csv`. The task supplies the complete placement and adjacency rules; there is no need to call `civ6lib` or apply additional Civ6 rules.

```python
import json, csv

with open("/root/work/map.json") as f:
    map_data = json.load(f)
with open("/root/work/city.json") as f:
    center = tuple(json.load(f)["city_center"])

tiles = {(t["x"], t["y"]): t for t in map_data["tiles"]}
```

For odd-r coordinates (odd rows shifted right), use the task’s neighbour offsets and cube-distance conversion:

```python
def neighbors(x, y):
    offsets = ([(1,0), (-1,0), (-1,-1), (0,-1), (-1,1), (0,1)]
               if y % 2 == 0 else
               [(1,0), (-1,0), (0,-1), (1,-1), (0,1), (1,1)])
    return [(x+dx, y+dy) for dx, dy in offsets]

def cube(x, y):
    cx = x - (y - (y & 1)) // 2
    cz = y
    return cx, -cx-cz, cz

def distance(a, b):
    return sum(abs(i-j) for i, j in zip(cube(*a), cube(*b))) // 2
```

Iterate **all supplied tiles** as potential sites. Require distance 1–3, terrain `GRASS` or `PLAINS`, feature other than `GEOTHERMAL_FISSURE`, and resource outside the strategic/luxury lists in the task. For adjacency, examine only neighbour coordinates present in `tiles`. Count `MOUNTAIN` under `terrain`; count `GEOTHERMAL_FISSURE`, `REEF`, `RAINFOREST`, and `WOODS` under `feature`. The adjacent city center counts as one district, **not** as woods or rainforest even if its tile has that feature.

Apply each `// 2` half-bonus **separately**—do not combine rainforest/woods and district counts before flooring. With only the city center as another district, its district half-bonus is zero. Evaluate sites independently; placing one Campus does not alter another site’s counts.

Sort rows with key `(-campus, -holy_site, y, x)`. Write via `csv.writer`, beginning with `["x", "y", "distance", "campus", "holy_site"]`; keep row values as integers.
