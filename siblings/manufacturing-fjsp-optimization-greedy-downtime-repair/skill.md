## Reference notes

Use Python’s standard-library `json` and `csv` modules. Read `instance.txt` as **whitespace-separated tokens**, not one job per line. Machine IDs are 1-based; job and operation IDs are 0-based.

```python
tokens = list(map(int, open("/root/work/instance.txt").read().split()))
it = iter(tokens)
J, M = next(it), next(it)
allowed = {}
for j in range(J):
    for o in range(next(it)):
        k = next(it)
        allowed[j, o] = {next(it): next(it) for _ in range(k)}  # machine -> duration
```

Load `baseline_solution.json` with `json.load(...)["schedule"]`. Preserve each row’s original list position for the processing-order tie-break:

```python
ordered = sorted(enumerate(baseline), key=lambda x: (x[1]["op"], x[1]["start"], x[0]))
```

Load downtime with `csv.DictReader`; convert `machine`, `start`, and `end` to integers. Keep downtime and already-placed operation intervals grouped by machine. Intervals are **half-open**:

```python
def overlap(s, e, a, b):
    return s < b and a < e
```

For each row in `ordered`, keep its baseline machine **if allowed**. Otherwise choose `min(allowed[j, o], key=lambda m: (allowed[j, o][m], m))`. Obtain duration from `allowed[j, o][machine]`, **not** baseline `dur`. The anchor is `max(baseline_start, newly_placed_end[j, o-1])` for `o > 0`, or `baseline_start` for `o == 0`. Starting at the anchor, increment integer `t` until `[t, t + duration)` conflicts with neither downtime nor previously placed work **on that machine**; record the placement immediately. Do not search alternate machines to improve the start: this task specifies a deterministic machine choice.

Finally sort recorded rows by `(job, op)` and write with `csv.DictWriter`, `fieldnames=["job", "op", "machine", "start", "end", "dur"]`, and `writeheader()`. Set `end = start + dur`. Check the row count against `len(allowed)` and confirm the output header and integer fields.
