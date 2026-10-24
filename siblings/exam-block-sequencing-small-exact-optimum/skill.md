## Exact approach

With 8 blocks, `itertools.permutations(blocks)` examines at most `8! = 40,320` schedules. Evaluate every feasible permutation and retain the lowest objective; this proves the chosen schedule is optimal without a solver.

Use `json` and `csv` from the Python standard library. `csv.DictReader` reads identifiers and counts as strings, so convert `count` to `int` and make tuple keys use the same identifier representation as `instance.json` (for example, `str(block)` for CSV lookups). Preserve block and slot labels when writing the output.

```python
from itertools import permutations
import csv, json

with open("/root/work/instance.json") as f:
    data = json.load(f)

def read_counts(path, columns):
    with open(path, newline="") as f:
        return {
            tuple(row[c] for c in columns): int(row["count"])
            for row in csv.DictReader(f)
        }

pairs = read_counts(
    "/root/work/pair_counts.csv", ("block_i", "block_j"))
triples = read_counts(
    "/root/work/triplet_counts.csv",
    ("block_i", "block_j", "block_k"))
```

`slot_order` defines chronology; slot labels are **not** arithmetic indices. Build `slot_index = {slot: i for i, slot in enumerate(slot_order)}`. For a permutation `seq`, the block at a start slot is `seq[slot_index[start]]`; its successors are at indices `i+1` and `i+2`. Score only the starts in `b2b_start` and `triple_start`, respectively:

```python
pair_total = sum(
    pairs.get((str(seq[i]), str(seq[i + 1])), 0)
    for start in data["b2b_start"]
    for i in (slot_index[start],)
)
triple_total = sum(
    triples.get((str(seq[i]), str(seq[i + 1]), str(seq[i + 2])), 0)
    for start in data["triple_start"]
    for i in (slot_index[start],)
)
objective = (data["weights"]["b2b"] * pair_total
             + data["weights"]["triple"] * triple_total)
```

Tuple keys are ordered: never sort, reverse, or symmetrize them. Missing CSV rows contribute zero. Do not wrap successors from the last slot to the first.

For each permutation, reject it unless every block in `large_blocks` occupies a slot in `early_slots`; then compare its objective to the best seen. Write the best permutation with `csv.writer`: header `slot,block`, followed by `zip(slot_order, best_permutation)`. Reload `schedule.csv` and check that its slots and blocks each occur exactly once, the early-slot restriction holds, and its independently recomputed objective equals the retained minimum.
