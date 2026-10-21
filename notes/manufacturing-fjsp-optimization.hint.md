1. `ls /app/data`, head instance.txt (FJSPLib: jobs line `nOps, k, (m,t)×k`), downtime.csv, baseline, and policy.json budgets. Check whether machine ids are 0- or 1-indexed.
2. In one Python script, repair in order `(op, base_start, idx)`: `anchor = max(base_start, prev_end)`, scan +1 per integer to avoid machine and downtime overlap, keep the baseline machine (replace it if illegal), and try alternates only if `shift >= THRESH` and the MC budget remains.
3. Validate precedence, overlaps, downtime, MC/Shift_L1 within budget, and makespan below the baseline.
4. Write /app/output/solution.json `{status, makespan, schedule[...]}` and an identical schedule.csv (job,op,machine,start,end,dur), then spot-check both files with head.
