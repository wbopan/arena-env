## Reference notes

Use Python’s standard-library `csv`, `json`, `re`, and `pathlib` to read the supplied files directly. The lookup skills are unnecessary: `distance.csv` already contains the leg records, and `cities.txt` supplies state membership.

```python
from pathlib import Path
import csv, json, re

root = Path("/root/work")
trip = json.loads((root / "trip.json").read_text())
with (root / "distance.csv").open(newline="") as f:
    rows = list(csv.DictReader(f))
```

- `cities.txt` is **tab-separated** with `State` and `City` entries. Check that the start, end, and every stop occur under `Ohio`.
- Index driving records by `(origin, destination)`. **Do not** infer `(B, A)` from `(A, B)`: directions are separate records. A consecutive pair needs its own direct record.
- Parse `H hours M mins` as `60 * H + M`, and `N km` as integer kilometers. For example, `re.fullmatch(r"(\d+) hours (\d+) mins", value.strip())` captures hours and minutes; validate the match before converting.
- Minimize the tuple `(total_duration_min, total_distance_km, tuple(stop_names_in_order))` lexicographically. The stop-name tie-break covers **stops only**, not start and end.
- For a small stop list, compare permutations. For a larger one, use subset dynamic programming: a state `(visited_stops, last_stop)` retains the best `(duration, distance, stop_order)` for reaching `last_stop`; extend only along existing directed legs, then add the leg to `end` when all stops are visited.
- Construct `ordered_city_names` as start, chosen stops, end. Build `legs` from adjacent names in that order, and sum those leg values for the integer totals. Write the single JSON object to `/root/work/route.json`.
