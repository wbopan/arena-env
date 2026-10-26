## Reference notes

Use Python’s standard-library `csv` and `collections.deque`; Lean tooling does not apply. Treat names as opaque strings. Do not strip whitespace, parse names as expressions, or infer reverse edges.

```python
import csv
from collections import defaultdict, deque

with open('/root/work/lemmas.csv', newline='', encoding='utf-8') as f:
    implications = list(csv.DictReader(f))

with open('/root/work/goals.csv', newline='', encoding='utf-8') as f:
    goals = list(csv.DictReader(f))  # retains input order
```

Build a directed adjacency list from `premise` to `conclusion`. Deduplicate repeated edges and sort each node’s neighbors by name. For each goal, breadth-first search from `known` using a FIFO `deque`; record each node’s predecessor **when first discovered**. With sorted neighbors, first discovery selects the lexicographically smallest name sequence among shortest paths. A visited/predecessor map prevents cycles from causing repeated work. Handle `known == target` as the zero-step path even if the name has no edges. If unreachable, use an empty chain.

Reconstruct a reached path by following predecessors from target back to known, reversing the resulting list, then joining with `'>'`. Compare names as strings, not joined path text.

Write with `csv.DictWriter(..., fieldnames=['goal_id', 'status', 'chain'])`, `writeheader()`, and one row per goal in input order. Open the output with `newline=''` to avoid CSV newline issues. Inspect the input headers briefly before coding; after running the script, check the output header and row count without dumping large files.
