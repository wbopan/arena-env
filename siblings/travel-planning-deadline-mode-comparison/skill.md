## Reference notes

Use Python’s standard-library `csv` module to read the three local files and write `modes.csv`; the search-skill lookup APIs are unnecessary because the task supplies the tables directly.

```python
import csv
from pathlib import Path

root = Path("/root/work")
with (root / "requests.csv").open(newline="", encoding="utf-8") as f:
    requests = list(csv.DictReader(f))  # preserves input order

with (root / "modes.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["date", "origin", "destination", "mode",
                    "service_id", "cost_usd", "duration_min"],
    )
    writer.writeheader()
    # writer.writerow(...) once per request
```

- Inspect a few raw rows before parsing, especially date and numeric formats. Match **directed** origin/destination pairs and flight dates; do not reverse a route.
- Parse driving duration `H hours M mins` as `60 * H + M`, and extract the integer kilometers from `N km`. Driving cost is `distance_km * 15 // 100 + toll_usd` for **one vehicle**, not per traveler.
- Flight duration comes from `ActualElapsedTime`, not the difference between `DepTime` and `ArrTime`. Flight cost is `2 * Price`; `decimal.Decimal` avoids floating-point rounding if prices contain decimals.
- Keep candidates only when `duration_min <= max_minutes`. Select with the key `(cost_usd, duration_min, mode, service_id)`. Write integer costs and durations, with no extra columns or index.
- A compact workflow: inspect headers/sample rows → parse and group directed routes/flights → process requests in their original order → write the CSV → reopen it to check its header and row count.
