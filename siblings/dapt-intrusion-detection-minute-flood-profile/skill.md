## Reference notes

Use Python’s standard-library `csv`, `collections.Counter`, `decimal.Decimal`, and `json`. This is a CSV packet log, not a PCAP: count **every data row**, including ARP. Only `ts` is needed; rows are shuffled.

```python
import csv
from collections import Counter
from decimal import Decimal

with open('/root/work/traffic.csv', newline='') as f:
    timestamps = [Decimal(row['ts']) for row in csv.DictReader(f)]

start = min(timestamps)
counts = Counter(int((ts - start) // Decimal(60)) for ts in timestamps)
```

`//` gives the required floor minute index without floating-point boundary drift. Iterate over `sorted(counts)` for output; do **not** add missing minute indices. Let `total = sum(counts.values())`, `occupied = len(counts)`, and `peak = max(counts.values())`. The unrounded average is `total / occupied`; to apply the strict DoS threshold without rounding, use the equivalent comparison `peak * occupied > 20 * total`. Equality is false.

For JSON numeric fields, round the average and each `100 * count / total` share to three decimal places. Write one JSON object to `/root/work/minute_profile.json` with exactly the requested keys, bucket keys, and JSON boolean; `json.dump(...)` writes Python `True`/`False` as JSON booleans.
