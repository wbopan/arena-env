## Reference notes

Use Python’s standard-library `json`, `csv`, `collections.Counter`, and `itertools.product`. This is **reconciliation, not schedule optimization**: keep every observed schedule unchanged.

- Read `slot_order` from `instance.json`; use it to access each observation’s slot columns in chronological order. The other JSON field, `blocks`, names the blocks.
- Treat `(first, second)` as a **directed** key. Never sort keys, substitute a reverse count, or sum both directions for one adjacency.
- For an observed schedule `sequence`, its contributing keys are exactly `zip(sequence, sequence[1:])`: five pairs for six slots, with **no last-to-first pair**.
- Build a `dict[(first, second)] -> int(count)` from `pair_counts.csv`. Keep the rows of `missing_pairs.csv` in their original order. Missing counts are unknowns, **not zeros**.

Each observation gives an integer equation. Count how often each missing directed pair occurs in its five adjacencies, then subtract known contributions from `total`:

```python
from collections import Counter

sequence = [row[slot] for slot in slot_order]
adjacencies = Counter(zip(sequence, sequence[1:]))
residual = int(row["total"]) - sum(
    multiplicity * known[pair]
    for pair, multiplicity in adjacencies.items()
    if pair in known
)
coefficients = [adjacencies[pair] for pair in missing_pairs]
# dot(coefficients, missing_counts) == residual
```

An exact, small search is sufficient for four unknowns in `1..6`: `itertools.product(range(1, 7), repeat=len(missing_pairs))`. Retain only candidates satisfying **every** observation equation with integer arithmetic; require exactly one candidate. Recompute each observed total directly from the complete directed-count dictionary as a final consistency check.

Write `/root/work/inferred_pairs.csv` with `csv.writer`, header `first,second,count`, and one row per missing pair **in input order**. Write counts as integers; do not add an index, extra columns, or other pair rows.
