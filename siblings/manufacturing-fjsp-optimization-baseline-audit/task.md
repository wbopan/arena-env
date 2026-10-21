A planner has produced a baseline schedule for a flexible job shop. You must audit it before it is released to the floor.

Inputs in /root/work:
- `instance.txt`: an FJSPLib-style instance. Read it as whitespace-separated tokens. The first two tokens are J (number of jobs) and M (number of machines). Then, for each job, comes its number of operations. For each operation comes k, followed by k pairs `machine duration`. These pairs are the allowed machines (numbered 1..M) and the processing time on each. Jobs and operations are indexed from 0 in file order.
- `downtime.csv`: columns `machine,start,end`. The machine is unavailable on [start, end).
- `baseline_solution.json`: `{"schedule": [{"job", "op", "machine", "start", "end", "dur"}, ...]}`, with one row per operation.

All intervals are half-open [start, end). Two intervals overlap iff s1 < e2 and s2 < e1.

Compute the following, using each row's `start` and `end`:
- `makespan`: the maximum end.
- `illegal_machine`: the number of rows whose machine is not allowed for that operation.
- `duration_mismatch`: the number of rows with an allowed machine where end - start differs from that machine's processing time.
- `precedence_violations`: the number of (job, op) where the end of op is greater than the start of op+1 of the same job.
- `machine_overlaps`: the number of unordered pairs of rows on the same machine whose intervals overlap. Count every row here, including rows with an illegal machine.
- `downtime_violations`: the number of rows overlapping at least one downtime window of their machine.
- `feasible`: true iff all five counts above are 0.

Write `/root/work/audit.json` as one JSON object with exactly these seven keys. The makespan and counts are integers; `feasible` is a JSON boolean.
