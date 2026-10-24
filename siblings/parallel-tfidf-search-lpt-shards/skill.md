## Reference notes

Use Python’s standard-library `json` and `re`; no parallel execution is needed to reproduce this deterministic assignment.

- JSONL is **one JSON object per line**, not one JSON array. Read line by line with `json.loads(line)`; read `config.json` with `json.load(file)`. Write the result with `json.dump(result, file)`.
- Tokenize with `re.findall(r"[a-z0-9]+", text.lower())`. Count **all** matches for cost, including repetitions. Use a `set` to count distinct terms; do not use the set’s size as the cost.
- LPT ordering: `sorted(documents, key=lambda d: (-d.cost, d.doc_id))`. The second key gives ascending, case-sensitive Python string order for tied costs.
- Maintain loads and document-ID lists indexed by worker number. For each sorted document, `min(range(K), key=lambda i: (loads[i], i))` selects the least-loaded worker and breaks ties by lowest index. Append its ID **when assigned**, then increase that worker’s load.
- `num_terms` is the size of the union of token sets for documents assigned to that worker, not the sum of per-document distinct counts. Empty workers have an empty ID list, zero load, and zero terms.
- `makespan = max(loads)`; for nonzero total cost, `imbalance = round(makespan / (total_cost / K), 4)`. The task does not specify a value when total cost is zero.

A compact workflow: inspect the config and a few JSONL lines; read/tokenize documents while retaining their costs and terms; sort and assign; build all `K` worker records in index order; write `schedule.json`; reopen it to check its structure and document ordering.
