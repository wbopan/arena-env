## Reference notes

Use Python’s standard-library `json`; no Azure SDK or graph library is needed. This input is a **functional directed graph**: each key ASN has at most one outgoing prefer-via link.

```python
import json

with open("/root/work/preferences.json", encoding="utf-8") as f:
    raw = json.load(f)

pref = {int(asn): (None if via is None else int(via))
        for asn, via in raw.items()}
```

- JSON object keys are strings; convert them to integers before numeric sorting and comparison.
- `null` ends a chain. A preferred ASN absent from `pref` also ends a chain; it is **not** a key ASN to classify.
- A self-preference is a one-member cycle. Do not skip it.
- A cycle contains only the nodes on the repeating portion of a chain. Nodes leading **into** it are affected, but not cycle members.

For each unclassified key, follow links while recording `path` and a local `{asn: index}` map. Reaching an ASN already in the local map identifies `path[index:]` as a new cycle; reaching `None`, an external ASN, or a previously classified ASN terminates the walk. Propagate the resulting affected/stable classification backward through the path. Caching classifications avoids repeatedly traversing long chains.

For output, rotate each cycle to start at its numeric minimum **without reversing its preference order**:

```python
i = cycle.index(min(cycle))
cycle = cycle[i:] + cycle[:i]
```

Sort cycles by their first member. Sort all ASN lists numerically. `oscillating_ases` is the union of cycle members; `affected_ases` includes those members and every key whose chain reaches them. `stable_ases` is the remaining set of keys. Set `oscillation_detected` from whether any cycles were found.

Write with `json.dump(report, file)`; Python integers become JSON numbers and booleans become JSON `true`/`false`. Before writing, check that affected and stable sets are disjoint and their union equals `set(pref)`.
