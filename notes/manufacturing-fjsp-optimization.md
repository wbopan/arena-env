**Inputs (all in /app/data/).** Run `ls -la /app/data` first, because the baseline file name is not given. It is probably something like `baseline_solution.json` or `baseline.csv`. Inspect each file cheaply:
- `head -5 instance.txt; wc -l instance.txt`
- `head -5 downtime.csv`
- `cat policy.json` (it is small)
- For a JSON baseline: `python3 -c "import json;d=json.load(open(P));print(d.keys() if isinstance(d,dict) else type(d));print(str(d)[:400])"`

**instance.txt is in FJSPLib format.**
- Line 1: `nJobs nMachines [avgMachinesPerOp]`.
- Each following non-empty line is one job: `nOps`, then for each op `k`, followed by k pairs `machine time`.
- Parse the job line as a flat integer stream with a pointer.
- FJSPLib machines are 1-indexed. Compare with the machine ids used in the baseline and downtime.csv, and convert if they are 0-indexed. Do the same check for job/op indexing (0 or 1 based).
- Build `allowed[(j,o)] = {machine: dur}`.

**Other inputs.**
- **downtime.csv:** expect columns like machine, start, end. Build `downtime[m] = sorted([(start,end), ...])`. Treat intervals as half-open: `overlap(s,e,a,b) = s < b and a < e`.
- **policy.json:** read the budget keys, e.g. max machine changes and max total L1 start shift. Print them and use the exact names.
- **Baseline:** a list of records with job, op, machine, start (and possibly end/dur). It may be infeasible:
  - it may use illegal machines;
  - it may have precedence violations;
  - it may have overlaps or downtime clashes.

**Constraints to satisfy.**
- Precedence: `end(j,o) <= start(j,o+1)`.
- No overlap of two ops on the same machine.
- No overlap with that machine's downtime windows.
- Each op uses a machine from `allowed[(j,o)]`, and `dur = allowed[(j,o)][machine]` (`end = start + dur`).
- Every op must be scheduled exactly once.
- Machine changes: `MC = Σ [m_new ≠ m_base] <= budget`.
- Start shift: `Shift_L1 = Σ |start_new − start_base| <= budget`.
- The policy must be no worse than the baseline, and the makespan (max end) should be below the baseline's.

**Repair procedure (follow it exactly; the evaluator simulates step by step).**
1. **Repair order.** Sort the keys by `(op, base_start, base_index)`:
   ```python
   keys.sort(key=lambda k:(k[1], base_map[k]["start"], base_index[k]))
   ```
2. **Anchor.** For each (j,o) in that order: `anchor = max(base_start, end_new(j,o-1))` (use 0 for the first op). Never start earlier than the baseline.
3. **Baseline machine.** Take `base_m`. If it is not in `allowed[(j,o)]`, replace it with `min(allowed, key=dur)`.
   - Count a machine change against the original baseline machine (`mm != base_m_orig`).
   - Note that a forced replacement then counts as a change automatically.
4. **Earliest start per candidate machine.** Scan integer time from the anchor upward by +1 until there is no conflict with the already-placed intervals on m or with downtime on m. Do not jump to gaps; the minimality rule is that start−1 must be infeasible.
   ```python
   t=anchor
   while has_conflict(m,t,t+d): t+=1
   ```
5. **Candidate selection.**
   - First evaluate `base_m`.
   - If `(start − base_start) >= THRESH` (try 6; tune 3–10) and `mc_used < max_mc`, evaluate all allowed machines.
   - Score each with `(machine_change, abs(st-base_start), st, mm)`.
   - Accept the alternate only if it starts earlier (smaller shift), and only while the MC budget remains.
6. **Record immediately.** Append `(st, st+d)` to `machine_intervals[mm]` and set `end_new[(j,o)]`, before moving to the next op.

**After building, validate in the same script.**
- Recompute precedence, machine overlaps, downtime overlaps, durations, MC, Shift_L1 and makespan.
- Print MC vs budget, Shift vs budget, and new vs baseline makespan. Print the baseline's MC=0/shift=0 reference too.
- If a budget is exceeded or the makespan is not better, adjust THRESH (e.g. loop over 1..15) and keep the best valid result: within budgets, smallest makespan, then smallest shift.

**Outputs (create the folder first with `mkdir -p /app/output`).**
- **/app/output/solution.json:**
  ```json
  {"status": "FEASIBLE", "makespan": <int max end>, "schedule": [{"job":j,"op":o,"machine":m,"start":s,"end":e,"dur":d}, ...]}
  ```
  - Use plain ints.
  - Use the same job/op/machine indexing convention as the baseline.
  - Sort by (job, op) or by start, consistently.
- **/app/output/schedule.csv:** header `job,op,machine,start,end,dur`, then the identical rows, written with the `csv` module or pandas `index=False`.

**Plan (about 8 commands).**
1. `ls` and the heads above.
2. Write `/app/solve.py` with a heredoc: parsing, repair, validation, writing both outputs.
3. `python3 /app/solve.py`, which prints the metrics.
4. `head -c 400 /app/output/solution.json; head -3 /app/output/schedule.csv; wc -l /app/output/schedule.csv`. The CSV row count should equal the total number of ops plus 1.
5. Fix the indexing or THRESH if validation fails.
