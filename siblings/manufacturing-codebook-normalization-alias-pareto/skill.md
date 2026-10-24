## Reference notes

Use Python’s standard-library `csv`, `json`, and `collections.Counter`; no semantic matching or text segmentation is needed. Each log row is one record. Keep `product_id`, `station`, and `code` as strings.

```python
import csv, json
from collections import Counter

def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def normalize(text):
    return " ".join(text.lower().replace("-", " ")
                       .replace("_", " ").replace(".", " ").split())
```

Character-level Levenshtein distance uses insert, delete, and substitute at cost 1 each. A two-row dynamic-programming implementation is sufficient:

```python
def distance(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            curr.append(min(curr[-1] + 1, prev[j] + 1,
                            prev[j-1] + (ca != cb)))
        prev = curr
    return prev[-1]
```

Build aliases by **product**, retaining each `(normalized_alias, code)` pair. For a record, choose the pair minimizing `(distance(normalized_reason, normalized_alias), code)`; the second element implements the lexicographically smallest-code tie-break. With no aliases for that product, use `UNKNOWN`. If the chosen distance exceeds 2, use `UNKNOWN`.

Look up the *chosen* code’s codebook entry for its product. An empty `station_scope` permits every station; otherwise compare the record’s station against `station_scope.split("|")`. An incompatible chosen code becomes `UNKNOWN`—do not retry another alias. The codebook supplies valid codes’ `standard_label`; `UNKNOWN` has label `""`.

Count records per product before computing shares. Include every product found in logs, even if all its records are `UNKNOWN`. Emit only positive-count codes, sorted by `(-count, code)`, with `share = round(count / product_record_count, 4)`. Write `/root/work/pareto.json` with `json.dump(..., ensure_ascii=False)`; JSON counts remain integers and shares are numeric floats.
