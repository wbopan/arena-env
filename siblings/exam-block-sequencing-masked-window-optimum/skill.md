## Reference notes

Use Python’s standard library. With seven blocks, `itertools.permutations` can exhaustively compare schedules; no optimization package is needed. Iterate over `sorted(blocks)` so equal-burden schedules are encountered in lexicographic order, or compare `(burden, sequence)` explicitly.

```python
import csv, json
from itertools import permutations

with open("/root/work/instance.json") as f:
    instance = json.load(f)

with open("/root/work/pair_counts.csv", newline="") as f:
    pairs = {
        (r["first"], r["second"]): int(r["count"])
        for r in csv.DictReader(f)
    }
with open("/root/work/triple_counts.csv", newline="") as f:
    triples = {
        (r["first"], r["second"], r["third"]): int(r["count"])
        for r in csv.DictReader(f)
    }
```

Let `sequence[i]` be the block in `instance["slot_order"][i]`. Starts are **zero-based indices into that list**, not slot labels. For a feasible sequence, evaluate exactly:

```python
pair_total = sum(
    pairs[(sequence[i], sequence[i + 1])]
    for i in instance["pair_starts"]
)
triple_total = sum(
    triples[(sequence[i], sequence[i + 1], sequence[i + 2])]
    for i in instance["triple_starts"]
)
burden = pair_total + 3 * triple_total
```

Preserve tuple order: do not sort tuple keys or add reverse tuples. Count only listed starts; do not wrap around. Every large block must have a slot label in `early_slots`. Before writing, check the chosen sequence is a permutation of `blocks`, has the required early placements, and has the lowest `(burden, sequence)` among feasible sequences.

Write only `/root/work/schedule.csv` using `csv.writer`, with header `slot,block` and rows from `zip(instance["slot_order"], sequence)`. Reopen that CSV and check its header, row order, assignments, and recomputed burden against the chosen sequence.
