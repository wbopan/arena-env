## Reference notes

Seven blocks have only `7!` possible orders, so use `itertools.permutations` for an exact enumeration; a MIP solver is unnecessary. Filter infeasible schedules before counting costs.

```python
import csv, itertools, json
from collections import Counter
from pathlib import Path

root = Path("/root/work")
instance = json.loads((root / "instance.json").read_text())
slots = instance["slot_order"]          # chronological order; do not sort
blocks = instance["blocks"]
large = set(instance["large_blocks"])
early = set(instance["early_slots"])

def read_counts(path, columns):
    with path.open(newline="") as f:
        return {
            tuple(row[col] for col in columns): int(row["count"])
            for row in csv.DictReader(f)
        }

pairs = read_counts(root / "pair_counts.csv", ("first", "second"))
triples = read_counts(root / "triple_counts.csv",
                      ("first", "second", "third"))
```

Ensure block identifiers used as CSV keys match the JSON identifiers’ representation (CSV fields are strings). A permutation’s index corresponds to the same index in `slot_order`; a large block is eligible only where that slot belongs to `early_slots`.

For a sequence `s` of length `n`, evaluate **ordered, nonwrapping** windows:

```python
pair_cost = sum(pairs[(s[i], s[i + 1])] for i in range(n - 1))
triple_cost = sum(triples[(s[i], s[i + 1], s[i + 2])]
                  for i in range(n - 2))
```

Do not sort tuple keys, add reverse directions, or count other triples within a wider span. The CSVs contain every ordered tuple of distinct blocks, so a missing lookup indicates an input/key mismatch.

Count each feasible permutation under its exact `(pair_cost, triple_cost)` key with `Counter`. After aggregation, sort distinct cost pairs by increasing pair cost. A pair is nondominated iff no *other* pair has both costs no greater, with at least one strictly smaller. In the sorted scan, retain a pair only when its triple cost is **strictly less** than every previously seen triple cost; equal triple costs at higher pair cost are dominated. Preserve the `Counter` value as multiplicity—do not count only one representative schedule.

Write just `frontier.json` with top-level key `"frontier"` and integer `pair_cost`, `triple_cost`, and `multiplicity` fields. Reload it once to check the JSON structure, ordering, and integer types.
