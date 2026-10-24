## Reference notes

Use Python’s standard-library `csv` and `json`; no Azure tooling is needed for this file-based audit.

- A relationship row `A,B,customer` means **B is A’s customer**. Store `type[(A, B)] = "customer"` and `type[(B, A)] = "provider"`. Swap `customer`/`provider` for the reverse view; `peer` remains `peer`.
- Look up types **from the interior AS’s perspective**: `source_type = type[(leaker_as, source_as)]` and `destination_type = type[(leaker_as, destination_as)]`. Do not infer them from the path’s direction alone.
- Check only indices `range(1, len(as_path) - 1)`. A path with fewer than three ASNs has no interior export to check.
- Valley-free rule: customer-learned routes may go to anyone; peer- or provider-learned routes may go **only to customers**. Thus both types being in `{"peer", "provider"}` identifies a leak.

```python
import csv
import json

reverse = {"customer": "provider", "provider": "customer", "peer": "peer"}
with open("/root/work/relationships.csv", newline="") as f:
    for row in csv.DictReader(f):
        a, b = int(row["as_a"]), int(row["as_b"])
        rel = row["relationship"]
        # Store (a, b) -> rel and (b, a) -> reverse[rel].

with open("/root/work/propagations.json") as f:
    paths = json.load(f)
```

Keep each detected row together with its interior-path index; sort by `(path_id, index)` before writing. Use `csv.writer` with `newline=""`, write the specified header unconditionally, then write one row per leak. `csv.writer` serializes integer ASNs as plain decimal values.
