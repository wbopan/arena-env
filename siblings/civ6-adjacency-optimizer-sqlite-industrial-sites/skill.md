## Reference notes

Use Python’s standard-library `sqlite3` and `csv`; the task specifies the schema and scoring rules, so no Civ6 rules engine is needed. Inspect cheaply with a few `SELECT ... LIMIT 5` queries if necessary, then read each of the three tables once.

```python
import sqlite3
con = sqlite3.connect("/root/work/industry.sqlite")
con.row_factory = sqlite3.Row
cities = list(con.execute("SELECT city_id, x, y FROM Cities"))
tiles = list(con.execute(
    "SELECT tile_id, x, y, terrain, resource, improvement FROM Tiles"))
built = list(con.execute("SELECT city_id, district, tile_id FROM Built"))
```

Index tiles by both `tile_id` (for `Built` links) and `(x, y)` (for spatial lookups). Make a set of **all** built tile IDs for eligibility, a set of built `AQUEDUCT` tile IDs, and a set of district coordinates containing **every city center and every built tile**. Do not restrict these sets to the city being evaluated.

Odd-r hex distance (odd rows shifted right):

```python
def cube(x, y):
    a = x - (y - (y & 1)) // 2
    return a, -a - y, y

def distance(p, q):
    return sum(abs(a - b) for a, b in zip(cube(*p), cube(*q))) // 2
```

For each city, consider map tiles with distance **1 or 2** from its center. Exclude its center, *any* tile in `Built`, `terrain == "MOUNTAIN"`, and `resource == "IRON"`. The task’s restrictions override broader placement rules in the skill documents.

For each eligible site, count only **existing map tiles** at distance 1. With counts from those neighbors, compute:

```text
bonus = 2 * aqueduct_count + quarry_count
        + mine_count // 2 + lumber_mill_count // 2
        + district_count // 2
```

`AQUEDUCT` is identified through `Built`; `QUARRY`, `MINE`, and `LUMBER_MILL` are tile improvements. Count city centers and built tiles as districts, but not the hypothetical site. Floor the three pair categories **separately**. Score every site against the original, unchanged map; sites selected for other cities add nothing.

Select by `(−bonus, y, x)` so ties favor smaller `y`, then smaller `x`. Write cities in ascending `city_id` order using `csv.writer` with `open(..., "w", newline="")`; the header is exactly `city_id,x,y,bonus`. Check the header, row count, ordering, and integer fields after writing.
