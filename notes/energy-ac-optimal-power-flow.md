**Inputs (inspect cheaply first).** Read `math-model.md` in full with `cat`. It is short, and it is the authority on the objective, the constraints and any reserve terms. The network is a large MATPOWER/PGLib JSON, typically `/root/network.json`; run `ls /root` to confirm. Never print it or use head/sed on it. Summarize it with Python instead:
```
python3 -c "import json;d=json.load(open('/root/network.json'));print(d.keys(),d['baseMVA'],len(d['bus']),len(d['gen']),len(d['branch']),d['gencost'][0])"
```
Check whether `reserve_capacity` and `reserve_requirement` are present, and whether math-model.md uses them.

**MATPOWER columns (0-based).**
- **bus:** 0 id, 1 type (3 = slack), 2 Pd (MW), 3 Qd, 4 Gs (MW at V=1), 5 Bs (MVAr at V=1), 7 Vm, 8 Va (deg), 11 Vmax, 12 Vmin.
- **gen:** 0 bus, 1 Pg, 2 Qg, 3 Qmax, 4 Qmin, 5 Vg, 7 status, 8 Pmax, 9 Pmin.
- **branch:** 0 f, 1 t, 2 r, 3 x, 4 b (total charging), 5 rateA (MVA, 0 = no limit), 8 tap (0 means 1.0), 9 shift (deg), 10 status, 11 angmin, 12 angmax (deg).
- **gencost:** model 2 is polynomial. Column 3 holds ncost, followed by coefficients from highest order down. Cost is evaluated with Pg in MW: c2·P² + c1·P + c0.

Bus numbers may be non-contiguous, so build `idx = {int(b[0]): i}`. Skip gens and branches whose status is 0 (or follow math-model.md).

**Libraries.** Use numpy and CasADi + IPOPT. If they are missing:
```
apt-get install -y -qq libgfortran5
pip install numpy==1.26.4 casadi==3.6.7
```

**Variables (per unit internally).**
- Vm in [Vmin, Vmax].
- Va is free, except the slack bus has Va = 0 (set lbx = ubx = 0).
- Pg in [Pmin, Pmax]/base.
- Qg in [Qmin, Qmax]/base.
- Optional reserves r in [0, rbar], with Pg + r ≤ Pmax and Σr ≥ R, if the model says so.

The objective uses MW: `Pmw = Pg*base`.

**Branch pi model** (from the skill; use exactly):
- Series admittance: g = r/(r²+x²), b = −x/(r²+x²). If r = x = 0, set g = b = 0.
- Tap and shift: tap = 1 if |tap| < 1e-12. it = 1/tap. sh = deg2rad(shift).
- Angle differences: δij = θi − θj − sh, and δji = θj − θi + sh.
- From-side flows:
  - Pij = g Vi² it² − Vi Vj it (g cos δij + b sin δij)
  - Qij = −(b + bc/2) Vi² it² − Vi Vj it (g sin δij − b cos δij)
- To-side flows:
  - Pji = g Vj² − Vi Vj it (g cos δji + b sin δji)
  - Qji = −(b + bc/2) Vj² − Vi Vj it (g sin δji − b cos δji)

**Nodal balance at every bus.**
- Σ Pg − Pd − Gs·V² = Σ (flows leaving the bus)
- Σ Qg − Qd + Bs·V² = Σ Q leaving

Here Pd, Qd, Gs and Bs are divided by baseMVA.

**Limits.**
- Thermal: Pij² + Qij² ≤ (rateA/base)², and the same for the ji direction, only when rateA > 0.
- Angle difference: angmin ≤ θi − θj ≤ angmax, converted to radians. Skip it if the bounds are ±360 or 0.

**Vectorize (essential for large grids).** Build with `ca.SX` (or MX) and index with integer arrays:
```
Vf = Vm[f_idx]; Vt = Vm[t_idx]
```
Then do element-wise math with numpy coefficient arrays wrapped as `ca.DM`.

Aggregate to buses with sparse incidence matrices:
```
Cf = ca.DM.triplet(f_idx.tolist(), list(range(nl)), [1.0]*nl, nb, nl)
Cg = ca.DM.triplet(genbus.tolist(), list(range(ng)), [1.0]*ng, nb, ng)
P_bal = ca.mtimes(Cg,Pg) - Pd - Gs*Vm**2 - ca.mtimes(Cf,Pij) - ca.mtimes(Ct,Pji)
```
`Ct` is built the same way as `Cf`, using `t_idx`. Make g = vertcat(P_bal, Q_bal, Sf, St, angdiff) with matching lbg/ubg arrays.

**Solver call.**
```
ca.nlpsol('s','ipopt',{'x':x,'f':obj,'g':g},
  {'ipopt.print_level':5,'ipopt.max_iter':3000,'ipopt.tol':1e-6,
   'ipopt.acceptable_tol':1e-4,'ipopt.mu_strategy':'adaptive','print_time':False})
```
- **Starting point:** Vm and Va (radians) from the bus data, Pg and Qg from the gen data, all clipped to their bounds, with slack Va = 0. Fall back to a flat start (Vm = 1, Va = 0) if that fails.
- **Status:** read `solver.stats()['success']` and `['return_status']`. Write "optimal" only when it succeeded (Solve_Succeeded, or Solved_To_Acceptable_Level).
- **Long runs:** large cases can take minutes. Run in the background and poll:
  `nohup python3 solve.py > log.txt 2>&1 &`, then `tail -3 log.txt`.
  Keep print_level 5 but only ever tail the log.

**Post-processing in numpy (recompute, don't trust the solver).**
- Recompute all branch flows from Vm and Va.
- Mismatches: max |P_bal|·base and max |Q_bal|·base.
- Voltage violation: max(0, Vm − Vmax, Vmin − Vm).
- Branch overload: max(0, S − rateA) in MVA.
- Cost: Σ polynomial(Pg_MW).
- Totals:
  - total_load_MW = ΣPd and total_load_MVAr = ΣQd, over all buses, in MW/MVAr.
  - total_generation = ΣPg and ΣQg over in-service gens.
  - losses = gen_MW − load_MW.

**Output: `/root/report.json`** (the working dir given in the task; check it).
- **summary:** total_cost_per_hour, total_load_MW, total_load_MVAr, total_generation_MW, total_generation_MVAr, total_losses_MW, solver_status.
- **generators:** one entry per generator in data order, with id 1-based. Fields: bus (bus number), pg_MW, qg_MVAr, pmin_MW, pmax_MW, qmin_MVAr, qmax_MVAr.
- **buses:** one entry per bus. Fields: id (bus number), vm_pu, va_deg (degrees), vmin_pu, vmax_pu.
- **most_loaded_branches:** about the top 10, sorted descending by loading_pct = 100·max(Sf, St)/rateA (only rateA > 0). Fields: from_bus, to_bus (bus numbers), loading_pct, flow_from_MVA, flow_to_MVA, limit_MVA.
- **feasibility_check:** max_p_mismatch_MW, max_q_mismatch_MVAr, max_voltage_violation_pu, max_branch_overload_MVA.

Convert everything to Python float/int; numpy types are not JSON-serializable. Keep at least 6 decimals.

**Pitfalls.**
- tap = 0 means 1.
- Angles in the data are in degrees.
- Shunt signs: −Gs·V² goes in the P balance, +Bs·V² in the Q balance.
- The cost is in MW, not per unit.
- Do not round prematurely.
- Do not print large arrays.

**Plan.**
1. `cat math-model.md`.
2. Run the JSON summary one-liner.
3. Write `solve.py` (build, solve, verify, write the report).
4. Run it in the background and tail the log.
5. Validate with a one-liner that loads report.json and prints the summary, the feasibility_check and the list lengths.

Mismatches should be about 1e-3 MW or less, and violations about 0. If not, debug signs and units, re-solve, and re-check.
