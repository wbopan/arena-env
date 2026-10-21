A maintenance disruption has made a flexible job shop baseline schedule infeasible. Repair it using the plant's standard deterministic right-shift procedure.

Inputs in /root/work:
- `instance.txt`: FJSPLib-style. Read it as whitespace-separated tokens. The first two tokens are J (jobs) and M (machines). Then, for each job, comes its number of operations. For each operation comes k, followed by k pairs `machine duration`. These pairs are the allowed machines (1..M) and the processing time on each. Jobs and ops are 0-indexed in file order.
- `downtime.csv`: columns `machine,start,end`. The machine is unavailable on [start, end).
- `baseline_solution.json`: `{"schedule": [{"job", "op", "machine", "start", "end", "dur"}, ...]}`, with one row per operation.

All intervals are half-open. Two intervals overlap iff s1 < e2 and s2 < e1.

Procedure:
1. Sort operations ascending by (op index, baseline start, position in the baseline list).
2. Process them in that order.
   - Machine: use the baseline machine if it is allowed for the operation. Otherwise use the allowed machine with the smallest processing time (ties: smallest machine id).
   - Duration: the instance processing time on the chosen machine. Ignore the baseline `dur` field.
3. Compute anchor = max(baseline start, new end of the same job's previous operation). For op 0, anchor = baseline start.
4. The start is the smallest integer t >= anchor such that [t, t+dur) overlaps neither a downtime window of the chosen machine nor any operation already placed on that machine by this procedure. Place the operation immediately.

Write `/root/work/repaired.csv`:
- The header is exactly `job,op,machine,start,end,dur`.
- Include one row per operation, sorted by job then op.
- All values are integers, with end = start + dur.
