## Reference notes

Use the supplied files directly with Python’s standard-library `json`, `csv`, and `itertools`; the attraction-search skill describes a separate city lookup and is not needed for this CSV.

```python
import csv, json
from itertools import product

with open("/root/work/visit.json", encoding="utf-8") as f:
    visit = json.load(f)

with open("/root/work/attractions.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
```

`DictReader` yields strings: convert `AdmissionUSD` and `Score` with `int()`. Keep `Name`, `City`, and `Category` unchanged so output capitalization matches the input. Build one list of rows per city **in `visit["cities"]` order**, then consider one row from each list using `product(*city_lists)`.

A combination is feasible when its categories are all distinct and its admission sum is `<= visit["budget_usd"]`. To rank feasible combinations with `min`, use the key `(-total_score, total_admission, tuple_of_names_in_city_order)`: it maximizes score, then minimizes admission, then selects the lexicographically smallest name tuple.

Write one JSON object to `/root/work/sights.json`. Each `selected` object uses keys `city`, `attraction`, `category`, `admission_usd`, `score`; the two totals are integers. Use `json.dump(...)` and check the written file’s city order, selections, and totals.
