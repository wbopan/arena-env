## Reference notes

Use Python’s standard-library `json` and `csv`; no browser or Playwright measurement is needed because the shifts are already recorded.

- JSONL is **one JSON object per line**, not one JSON array. Read lines individually with `json.loads(line)` and group counted entries by `page`. Exclude `hadRecentInput: true` before sorting or counting.
- Sort each page’s counted entries by numeric `startTime`. For a window beginning at `first` with previous counted shift at `previous`, the next shift at `t` joins **only if** `t - previous < 1000` **and** `t - first < 5000`. Equality at either limit starts a new window. Compare against the previous shift, not just the window start.
- Sum `value` within each window. Retain the highest-scoring window and its first shift’s time; on an equal score, retain the earlier window. Comparing with `>` rather than `>=` while processing in time order preserves the earliest tie. `shift_count` is the total number of counted entries for the page, not the size of its worst window.
- Apply the task’s rating boundaries to the **unrounded** CLS: `<= 0.1` good; `<= 0.25` needs-improvement; otherwise poor. Format only when writing: `f"{cls:.4f}"`, `f"{window_start:.1f}"`.

```python
from collections import defaultdict
import csv
import json

by_page = defaultdict(list)
with open("/root/work/layout_shifts.jsonl", encoding="utf-8") as src:
    for line in src:
        if not line.strip():
            continue
        entry = json.loads(line)
        if not entry["hadRecentInput"]:
            by_page[entry["page"]].append(entry)

# For each page in sorted(by_page):
#   sort entries with key=lambda entry: entry["startTime"]
#   scan once, closing and comparing each completed window
#   compare the final window too
#   write the page's row with csv.writer
```

Write the exact header `page,cls,rating,shift_count,worst_window_start_ms` using `csv.writer` and open the destination with `newline=""`. After running the script, inspect the header and a few rows, and confirm rows are sorted by the page string.
