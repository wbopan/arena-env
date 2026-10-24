## Reference notes

Use Python’s standard-library `csv`, `collections.defaultdict`, and `math`. The input is **CSV, not PCAP**; Scapy and the PCAP helper are unnecessary.

```python
import csv
from collections import defaultdict
from math import sqrt

groups = defaultdict(list)
with open('/root/work/traffic.csv', newline='') as f:
    for row in csv.DictReader(f):
        src, dst = row['src_ip'], row['dst_ip']
        if not src or not dst:
            continue
        groups[(src, dst)].append((float(row['ts']), int(row['length'])))
```

- Keys are directed `(src_ip, dst_ip)` strings; do not include ports or protocol, and do not merge reverse directions.
- For each group with at least 10 packets, sort **its timestamps** before calculating consecutive differences. Packet count is the number of rows; bytes are the sum of `length`.
- For IATs `d`: `mean = sum(d) / len(d)`; population standard deviation is `sqrt(sum((x - mean)**2 for x in d) / len(d))`; `cv = std / mean` if the mean is nonzero, otherwise `0`.
- Classify using the **unrounded** value: `cv < 0.5`. Round mean to 3 decimal places and CV to 4 only for output.
- Iterate pairs with `sorted(groups)` for lexicographic source-then-destination order. Write with `csv.writer(..., newline='')`, the exact requested header, and `'true' if cv < 0.5 else 'false'` rather than Python’s capitalized boolean strings.

Write one script, run it, then inspect the output header and a few rows.
