**Goal and outputs.** Produce one permutation that assigns the 24 blocks to the 24 slots. The objective is minimized:

objective = 1·eve_morn_b2b + 1·other_b2b + 10·same_day_triple + 10·cross_day_triple + 5·z_three_in_four

Write these four files to `/root/output/` (create it with `mkdir -p`):
- `schedule.csv`
  - header `slot,block`, then exactly 24 rows, one per slot, in the instance's slot order.
  - Every block appears exactly once, including virtual blocks.
- `metrics.json`
  - keys: `objective`, `eve_morn_b2b_count`, `other_b2b_count`, `same_day_triple_count`, `cross_day_triple_count`, `z_three_in_four_count`.
  - Values must be numbers recomputed from the saved CSV.
- `formulation.md`: the MIP write-up described below.
- `report.md`: final objective, score breakdown, feasibility check, and method.

**Inspect cheaply first (never cat large files).**
- `cat /root/data/README.md`. This is the data contract and the most important read.
- `ls -la /root/data`
- `python3 -c "import json;d=json.load(open('/root/data/instance.json'));print({k:(type(v).__name__,len(v) if hasattr(v,'__len__') else v) for k,v in d.items()})"`
- `head -3` each CSV.
- Check which solver is installed: `python3 -c "import pyscipopt;print('scip ok')"`. Also try `pulp`, `ortools`, `highspy`.

From the README and instance, write down the following before coding:
- **Slot order.** Use the declared ordered list. Build `succ` from it. Do not assume labels are 0..23.
- **Start masks per component.** These are the eligible starts for each term: eve→morn b2b, other b2b, same-day triple, cross-day/24h triple, and the four-slot pressure term.
- **Count tables.**
  - Pair/triplet student counts, and whether they are keyed by ordered tuples. The default is ordered: use `(block_at[t], block_at[succ t], ...)` exactly.
  - Never sort or symmetrize keys, and never add reverse rows, unless the README says the table is unordered.
  - Missing rows count as 0 only if the README implies sparse tables.
- **The exact definition of the "three-in-four" / overlapping four-slot pressure term.** Do not invent it. Possible meanings:
  - an explicit 4-tuple table;
  - two overlapping active triple windows;
  - triples with span ≤4.
  
  Use only what the README or instance defines. Do not count "all combinations in a 4-window" unless that is stated.
- **Front-loading.** Note `large_blocks` and `early_slots` (or similar keys). If both are present and non-empty, every large block must sit in an early slot.
- **Virtual blocks.** Treat them as ordinary blocks to be placed.

**Pure evaluator, written first.** `evaluate(seq, data)` takes `seq` as a dict slot→block. For each component it loops over that component's eligible starts and builds the ordered tuple by following `succ`. It then adds the table value, defaulting to 0 only if the tables are sparse. It returns the counts plus the weighted objective.

Also write `validate(seq)`, which checks:
- 24 distinct slots and 24 distinct blocks;
- every block is present;
- front-loading holds.

Use these two functions for everything: the heuristic, auditing the solver result, and writing metrics.

**Solve with a hybrid that has the MIP as the main method.**
1. **Warm start by local search.** Start from a random feasible permutation (large blocks placed in early slots). Run simulated annealing with swap moves that preserve feasibility, scoring each move with the evaluator. Keep the best result over several restarts, within roughly 60 s.
2. **MIP in PySCIPOpt** (`from pyscipopt import Model, quicksum`).
   - **Variables:** binary `x[b,t]`.
   - **Assignment constraints:** `sum_t x[b,t]==1` for each block, and `sum_b x[b,t]==1` for each slot.
   - **Front-loading:** `x[b,t]=0` for each large block b and each non-early slot t. Equivalently, `sum_{t in early} x[b,t]==1`.
   - **Pair terms:** for each eligible start t and each pair (i,j) with count>0, create `y>=x[i,t]+x[j,succ t]-1` with y≥0. Weight it by count × component weight. Lower-bound linking is enough because we minimize.
   - **Triple terms:** do the same only for triples with count>0: `z>=x[i,t]+x[j,t1]+x[k,t2]-2`.
   - **Pressure term:** link exactly as defined, e.g. `w>=z_left+z_right-1` for overlapping active windows, or a 4-tuple `>= sum x - 3`.
   - **Keep the model small.** Create variables only for nonzero-count tuples and eligible starts.
   - **Run settings:** `model.setParam("limits/time", 600)`. Load the heuristic incumbent with `s=model.createSol(); model.setSolVal(s,x[b,t],1/0); model.addSol(s)`, or use `trySol`. Then call `model.optimize()`.
   - **Record:** `status=model.getStatus()`, `model.getObjVal()`, `model.getDualbound()`, `model.getGap()`, `model.getNSols()`.
   - **Extract:** `model.getSolVal(sol,x[b,t])>0.5` on `sol=model.getBestSol()`. Do not use `var.getVal()`.
3. **Audit.** Check that the evaluator objective on the extracted schedule equals the solver objective (|diff|<1e-6). If it differs, the linearization, keys, or masks are wrong; fix them before writing output.
4. **If the model is too large to solve,** reduce the time limit but keep all terms. Do not drop the high-order terms. Report honestly that the result is a time-limited incumbent.
5. **Post-processing.** If heuristic post-processing improves the result after the solve, disclose it and do not reuse the solver gap for it.

**Write outputs in this order.**
1. Write `schedule.csv`.
2. Reload it from disk, then run `validate` and `evaluate`.
3. Dump `metrics.json` from that reloaded evaluation, with ints for counts and a number for the objective.
4. Write the two markdown files from the same numbers.

**`formulation.md` contents.** Use the explicit words "minimize / minimization". Include:
- the decision variables (`x[b,t]`, pair y, triple z, overlap w: types and meanings);
- "each block assigned exactly once; each slot receives exactly one block; no duplicates or missing assignments";
- the front-loading/eligibility constraint (state it even if inactive), and that virtual blocks are treated as normal;
- the adjacent-pair burden terms (eve-morn and other b2b), the three-slot triple terms (same-day and cross-day/24h), and the overlapping four-slot pressure term, each with its linearization inequality and weight (1, 1, 10, 10, 5);
- the solver (SCIP via PySCIPOpt), time limit, status, incumbent, best bound, and gap;
- the warm-start heuristic, how the solution was extracted, and the independent audit.

Do not claim optimal unless the status is "optimal" or the gap is 0.

**`report.md` contents.**
- final objective and per-component counts with their weighted contributions;
- feasibility checks: 24/24 unique, all blocks placed, large blocks in early slots;
- the method summary and solver certificate.

**Pitfalls.**
- Using array index instead of the declared slot order.
- Applying cyclic wraparound.
- Sorting tuple keys.
- Double-counting both directions of a pair.
- Writing metrics from solver expressions.
- Printing big tables. Print only lengths and a couple of sample rows.
