## Reference notes

Use Python’s standard-library `json`; the inputs are already JSON, and placements are valid. No placement search or validation is needed. The task’s explicit adjacency rules take precedence over broader Civ6 rules in the skill documents.

```python
import json

with open("/root/work/map.json") as f:
    game_map = json.load(f)
with open("/root/work/layouts.json") as f:
    layouts = json.load(f)

tiles = {(t["x"], t["y"]): t for t in game_map["tiles"]}

def neighbors(x, y, width, height):
    if y % 2 == 0:
        offsets = [(1, 0), (-1, 0), (-1, -1),
                   (0, -1), (-1, 1), (0, 1)]
    else:
        offsets = [(1, 0), (-1, 0), (0, -1),
                   (1, -1), (0, 1), (1, 1)]
    return [(x + dx, y + dy) for dx, dy in offsets
            if 0 <= x + dx < width and 0 <= y + dy < height]
```

For **each layout independently**, make an occupied-coordinate set from its city center and three district positions. For each district, inspect only its six in-bounds neighbors. An adjacent occupied tile counts toward `districts`, including the city center. On occupied tiles, do **not** count `WOODS`, `RAINFOREST`, or any improvement; do not generally discard terrain or resources.

Count the named terrain, features, resources, and improvements according to their respective tile fields. Strategic resources are `IRON`, `COAL`, `HORSES`, `NITER`, `OIL`, `ALUMINUM`, `URANIUM`. Missing JSON values become Python `None`.

Apply `// 2` **separately to each half-bonus category**—never combine rainforest, woods, mines, lumber mills, or districts before flooring. Use only the three formulas in the task; other adjacency rules from the Civ6 reference are outside this audit.

Build one result per input layout in its original order, with integer bonuses and their sum as `total`; sum those totals for `grand_total`. Write the requested object using `json.dump(...)` to `/root/work/adjacency.json`, then inspect the written JSON and its layout count.
