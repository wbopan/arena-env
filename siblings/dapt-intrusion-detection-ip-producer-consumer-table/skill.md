## Reference notes

Use Python’s standard-library `csv` and `collections.defaultdict`. The PCAP helper functions expect packet objects, not CSV rows, so they are not needed here.

```python
import csv
from collections import defaultdict

with open('/root/work/traffic.csv', newline='') as f:
    for row in csv.DictReader(f):
        # Skip ARP rows (empty IP fields).
        # int(row['length']) is the captured byte count.
        # Do not require ports: IP packets may have empty port fields.
        ...
```

- Accumulate sent bytes by `src_ip` and received bytes by `dst_ip`; include IPs seen on **either** side. Timestamp order, protocol and ports do not affect these totals.
- Directed degrees count **unique neighbors**, not packets: maintain `out_neighbors[src].add(dst)` and `in_neighbors[dst].add(src)`. Opposite directions are separate edges.
- For each IP, `pcr = (sent - recv) / (sent + recv)` when the denominator is nonzero. Classify using the **unrounded** value: `> 0.2` producer, `< -0.2` consumer, otherwise balanced. Format PCR only when writing: `f'{pcr:.6f}'`.
- Write with `csv.writer` or `csv.DictWriter`, `newline=''`, and the specified header. Iterate `sorted(all_ips)` for text ordering; write no index or summary row.
