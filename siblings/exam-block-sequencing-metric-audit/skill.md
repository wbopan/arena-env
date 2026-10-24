## Reference notes

Use Python standard-library `json` and `csv`; no solver is needed because the schedule is fixed.

```python
from pathlib import Path
import csv, json

root = Path("/root/work")
with (root / "instance.json").open() as f:
    instance = json.load(f)

with (root / "schedule.csv").open(newline="") as f:
    schedule_rows = list(csv.DictReader(f))
```

CSV fields are strings. Normalize slot and block identifiers consistently across JSON and CSV (for example, with `str`) before using them as keys. Parse each `count` with `int`. Build pair and triplet lookup dictionaries using the CSV columns **in their given order**; use `lookup.get(key, 0)` for missing rows. Never sort keys or add reversed/permuted entries.

`slot_order` alone determines successors. Map each slot label to its index, then obtain offsets from that list—not from CSV row order, slot-label arithmetic, or wraparound:

```python
slots = [str(x) for x in instance["slot_order"]]
index = {slot: i for i, slot in enumerate(slots)}
block_at = {row["slot"]: row["block"] for row in schedule_rows}

def blocks_at(start, offsets):
    i = index[str(start)]
    return tuple(block_at[slots[i + offset]] for offset in offsets)
```

Check that the schedule fills each slot once and assigns each listed block once; a dictionary alone can hide duplicate CSV rows. For each component, iterate **only** its specified start list. Pair components use offsets `(0, 1)`; ordinary triples use `(0, 1, 2)`. Each `four_start` contributes exactly two ordered triplets, with offsets `(0, 1, 3)` and `(0, 2, 3)`—not every triple in the four-slot span.

Compute the weighted objective from the five integer component counts. Write a JSON object with the six requested integer fields to `/root/work/metrics.json`, then reopen it to confirm its contents.
