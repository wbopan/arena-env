## Reference notes

Use Python’s standard-library `json`, `csv`, and `collections.Counter`; this is **postprocessing**, not a new routing problem, so OR-Tools is unnecessary.

- Inspect the JSON structure briefly to confirm the route-list location and the trip pickup/dropoff field names. Preserve the candidate routes’ vehicle order.
- Read `t_matrix.csv` with `csv.reader`: it is **headerless**, so row 0 and column 0 are `DEP`. Convert every cell to `int`. Build the node-to-index mapping by walking `requests.json` in its listed **group order**, then each group’s **trip order**, adding each trip’s pickup followed by its dropoff. Check that the resulting node count matches the square matrix dimensions.
- Count occurrences across **both** candidate routes, excluding depot endpoints. For each trip, require exactly one occurrence of its pickup and exactly one of its dropoff in the entire plan; find their route and position, and require the same route with pickup position less than dropoff position. A group is complete only when **both trips** pass. Mere presence of all four nodes is insufficient.
- Retain only service nodes belonging to complete groups. Filter each original route without sorting its stops, and retain its opening and closing `DEP` even if no service nodes remain.
- Recalculate travel from consecutive nodes of each cleaned route: `sum(matrix[index[a]][index[b]] for a, b in zip(route, route[1:]))`. This includes the `DEP`→`DEP` arc for an empty route. Do not add service time or reuse a candidate-plan travel total.
- Write one JSON object with **only** `complete_group_ids` (alphabetically sorted), `cleaned_routes`, and `total_travel_min` (an integer).

Minimal file I/O pattern:

```python
import csv
import json
from pathlib import Path

base = Path("/root/work")
requests = json.loads((base / "requests.json").read_text())
candidate = json.loads((base / "candidate_routes.json").read_text())
with (base / "t_matrix.csv").open(newline="") as f:
    matrix = [[int(cell) for cell in row] for row in csv.reader(f)]

# After inspecting the JSON shapes, build node_index and evaluate each
# group's trips against (route_number, position) occurrences.
# Filter routes, then sum matrix costs over their consecutive node pairs.

(base / "cleaned_plan.json").write_text(json.dumps(result) + "\n")
```
