## Reference notes

Use Python’s standard-library `json`; no Civ6 library is needed because the task supplies the permitted spots and the complete scoring rules. Inspect the JSON’s top-level keys and a sample tile to identify the list names before writing the script. Index map tiles by `(x, y)` for cheap adjacency lookups.

```python
import json
from pathlib import Path

data = json.loads(Path("/root/work/pair_map.json").read_text())
print(data.keys())
```

Odd-r hex distance (odd rows shift right):

```python
def cube(x, y):
    a = x - (y - (y & 1)) // 2
    return a, -a - y, y

def distance(p, q):
    return sum(abs(a - b) for a, b in zip(cube(*p), cube(*q))) // 2
```

Only tiles at distance **1** are adjacent. For each distinct Campus/Holy Site pair from their respective permitted lists, score the map **after both placements**:

- A placed district clears `FOREST` or `JUNGLE` on its own tile. Do not count a cleared feature toward the other district’s bonus.
- Adjacent `MOUNTAIN` terrain: +1 each for either district.
- Campus: +2 per adjacent `GEOTHERMAL` feature, plus `adjacent_JUNGLE_count // 2`.
- Holy Site: `adjacent_FOREST_count // 2`.
- Either district: `adjacent_district_tile_count // 2`, counting the city center and the *other* new district when adjacent.
- Floor the feature-pair and district-pair counts **separately**; never combine them before division.

This is a two-list search, so evaluate every distinct pair rather than pruning candidates. Compare pairs by `(-total, campus_y, campus_x, holy_site_y, holy_site_x)` in ascending order. Write JSON containing **only** `placements`, `bonuses`, and `total`; use integer bonuses and `[x, y]` coordinate arrays.
