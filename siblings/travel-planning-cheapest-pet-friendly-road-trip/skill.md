## Reference notes

Use the supplied files directly with Python’s standard-library `csv`, `itertools`, `decimal`, and `json`. The relevant skill documents describe city, accommodation, and driving lookups, but reading these three files directly is simpler for comparing all possible routes.

```python
from pathlib import Path
import csv
from decimal import Decimal

root = Path("/root/work")
with (root / "accommodations.csv").open(newline="", encoding="utf-8") as f:
    listings = list(csv.DictReader(f))
with (root / "distance.csv").open(newline="", encoding="utf-8") as f:
    legs = list(csv.DictReader(f))
```

- Read `cities.txt` line by line; split each nonempty line on the **tab** into state and city. Keep only cities whose state is `Ohio`.
- A listing qualifies when `"No pets" not in row["house_rules"]`, `int(row["maximum occupancy"]) >= 2`, and `int(row["minimum nights"]) <= 2`. Its cost is `Decimal(row["price"]) * 2`. Keep the cheapest qualifying listing for each city; retain its exact `NAME`.
- Key driving legs by `(origin, destination)`. A reverse leg is **not** implied. Use `Decimal(row["cost"])`; `duration` and `distance_km` do not enter the objective.
- Iterate `itertools.permutations(eligible_ohio_cities, 3)`. For each `(A, B, C)`, require all four directed legs in `("Minneapolis", A, B, C, "Minneapolis")`. Add their costs once each, then add the three two-night listing costs. Retain a plan only when its total improves on the current minimum.
- Write `/root/work/trip.json` with `json.dump`, preserving accommodation names in route order. JSON costs must be numbers, not quoted strings. Do not round intermediate costs; convert `Decimal` values to JSON-compatible numeric types when writing. Check that the written file parses and that its component costs sum to its total.
