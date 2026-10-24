## Reference notes

Use Python standard library: `json` for JSONL, `collections.defaultdict` for per-key data, `bisect.bisect_right` for successor lookup, and `csv` for output.

- Treat each nonempty line as one event: `json.loads(line)`. **File order is not a timeline**; `ats` and `txn` are not needed for this classification.
- Build a per-key list of write `wts` values, then sort it. A key also has an implicit version at `wts=0`; it need not appear among logged writes.
- For an abort’s `local_wts = v`, the successor is the **smallest write `wts` strictly greater than `v` on the same key**. For a sorted list, `bisect_right(writes_by_key[key], v)` gives its index. Do not use `current_wts` as the successor: later writes may exist, and the current version is merely what triggered validation failure.
- The read version’s validity interval ends just before that successor: `[v, s)`. Classify the abort as unnecessary exactly when `commit_ts < s`. Equality with `s` is **necessary**. If there is no greater write timestamp, there is no finite successor, so the version has no recorded upper validity bound.
- Count **abort events**, not distinct transactions or `(txn, key)` pairs. Aggregate only keys with aborts, sort keys in string order, and format `unnecessary_aborts / total_aborts` with `f"{rate:.4f}"`.

Useful API fragments (adapt into one script):

```python
with open("/root/work/trace.jsonl", encoding="utf-8") as f:
    events = [json.loads(line) for line in f if line.strip()]
```

```python
from bisect import bisect_right

timestamps = sorted(writes_by_key.get(key, ()))
i = bisect_right(timestamps, local_wts)  # first timestamp > local_wts
successor = timestamps[i] if i < len(timestamps) else None
```

```python
import csv

with open("/root/work/abort_report.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["key", "total_aborts", "unnecessary_aborts", "rate"])
    # Emit one row per abort-bearing key, in sorted order.
```

Workflow: inspect a few input lines cheaply; collect and sort per-key write timestamps; classify every abort against its key’s successor; aggregate and write the CSV; inspect its header, row order, and four-decimal formatting.
