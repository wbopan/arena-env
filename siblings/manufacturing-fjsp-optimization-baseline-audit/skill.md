## Reference notes

Use Python standard-library `json` and `csv`; no scheduling or repair library is needed.

- Parse `instance.txt` as whitespace-separated integers. Consume `J, M`, then for each job consume its operation count; for each operation consume `k` followed by `k` `(machine, duration)` pairs. Store allowed processing times as `allowed[(job, op)][machine] = duration`. Job and operation indexes start at **0**; machine numbers remain **1-based**.
- Read `baseline_solution.json` with `json.load(...)["schedule"]`. Use each row’s `start` and `end` for every interval calculation. The row’s `dur` field does not determine its actual duration.
- Read downtime with `csv.DictReader`; convert `machine`, `start`, and `end` to integers. Group windows by machine.

```python
def overlap(s1, e1, s2, e2):
    return s1 < e2 and s2 < e1  # half-open intervals
```

Count rules:

- **Illegal machine:** one per row whose machine is absent from `allowed[(job, op)]`.
- **Duration mismatch:** only for rows on an allowed machine; compare `end - start` with that machine’s allowed duration.
- **Precedence violation:** for each adjacent pair of operations in a job, count one if `end(job, op) > start(job, op+1)`.
- **Machine overlap:** examine each unordered pair of distinct schedule rows once; count it if both rows name the same machine and their intervals overlap. Include illegal-machine rows.
- **Downtime violation:** count a row **once** if it overlaps *any* downtime window for its machine.
- Makespan is `max(row["end"] for row in schedule)`. Feasible is true exactly when all five violation counts are zero.

A short workflow: parse the instance and inputs; index schedule rows by `(job, op)` for precedence; count row-level issues, adjacent-operation issues, and unordered machine pairs separately; write one JSON object with the seven requested keys using `json.dump`.
