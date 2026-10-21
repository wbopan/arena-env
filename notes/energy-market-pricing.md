**Inputs and tools.** `network.json` is MATPOWER-style JSON. Its keys are `baseMVA`, `bus`, `gen`, `branch`, `gencost`, `reserve_capacity` (MW per generator) and `reserve_requirement` (MW). It may be large, so do not `cat`, `head` or `sed` it. Load it with `json.load` and print only a summary. Use numpy, scipy.sparse and cvxpy with `solver=cp.CLARABEL`. Write the output to `report.json` in the working directory.

**Column conventions (0-indexed).**
- bus: `[0]`=bus number, `[1]`=type (3 = slack), `[2]`=Pd in MW.
- gen: `[0]`=bus, `[7]`=status, `[8]`=Pmax, `[9]`=Pmin.
- branch: `[0]`=from, `[1]`=to, `[3]`=x, `[5]`=RATE_A in MW, `[10]`=status.
- gencost type 2: `[3]`=NCOST, then coefficients from highest order down.
  - NCOST=3 gives c2, c1, c0 and cost = c2·P² + c1·P + c0, with P in MW.
  - NCOST=2 gives c1, c0.

**Bus numbering.** Bus numbers are non-contiguous (this case has bus 1501). Always map them: `idx = {int(b[0]): i for i, b in enumerate(bus)}`. Never use `bus_num - 1`.

**Model.** Write it in vectorized, sparse form, because a dense B matrix for thousands of buses is slow.
- Variables: `Pg` (MW, n_gen), `Rg` (MW, n_gen) and `theta` (n_bus).
- Fix the slack angle with `theta[slack] == 0`.
- Branch flow in MW: `flow = baseMVA * (1/x) * (theta[f] - theta[t])`. Build it as `Bf @ theta`, where `Bf` is a sparse n_br×n_bus matrix with entries +b at (k, f) and −b at (k, t), scaled by baseMVA.
- Line limits: `-rate <= flow <= rate`. Apply them only where `rate > 0`; RATE_A = 0 means unlimited.
- Skip branches with status 0 or x = 0.
- Nodal balance, as one vector constraint so its dual gives all LMPs at once: `bal = (Cg @ Pg - Pd == Bf.T @ theta)`.
  - `Cg` is sparse n_bus×n_gen.
  - `Bf.T @ theta` is the net injection in MW because Bf already includes baseMVA.
  - Because the balance is in MW, the LMP is `bal.dual_value` directly, with no baseMVA scaling.
  - If you instead write the balance in per-unit, multiply the dual by baseMVA.
- Generator limits: `Pmin <= Pg <= Pmax`.
- Reserve limits: `0 <= Rg <= reserve_capacity`.
- Capacity coupling: `Pg + Rg <= Pmax`.
- System reserve: `res = (cp.sum(Rg) >= reserve_requirement)`. The reserve MCP is `float(res.dual_value)`, which should be ≥ 0.
- Objective: sum of `c2*cp.square(Pg) + c1*Pg + c0`, vectorized as `cp.sum(cp.multiply(c2, cp.square(Pg))) + c1 @ Pg + c0.sum()`. Total cost is `prob.value`, which includes c0.
- If any generator has status 0, either drop it or force Pg = Rg = 0. Keep the reserve_capacity indexing aligned with the gen rows.

**Sign check for LMPs.** In cvxpy the sign of an equality dual depends on how the constraint is written. After solving, compare a typical LMP with the marginal cost 2·c2·Pg + c1 of an unconstrained marginal generator. If the LMPs look mirrored (mostly negative), negate them. A few negative LMPs are legitimate under congestion.

**Binding lines.** For each in-service branch with rate > 0, compute `loading = |flow| / rate * 100`. A line is binding if loading ≥ 99. Record it as `{"from": int, "to": int, "flow_MW": signed flow, "limit_MW": rate}`, where limit_MW is the rate used in that scenario. In the counterfactual, the target line's limit is the raised value.

**Counterfactual.** Copy the branch array. Find every row where (from, to) is (64, 1501) or (1501, 64), print how many there are, and multiply RATE_A by 1.2. If there are parallel circuits, scale them all and note it. Then re-solve with the identical model.

**Impact analysis.**
- `cost_reduction = base_cost - cf_cost`. It should be ≥ 0, up to solver noise.
- For each bus, `delta = cf_lmp - base_lmp`. Sort ascending (most negative first) and take the top 3 as `{"bus", "base_lmp", "cf_lmp", "delta"}`.
- `congestion_relieved` is `True` if the 64–1501 line is NOT in the counterfactual binding list (loading < 99%), otherwise `False`.
- Also print whether the line was binding in the base case, as a sanity check.

**Output format.** `report.json` must have three top-level keys: `base_case`, `counterfactual` and `impact_analysis`.
- Each case contains `total_cost_dollars_per_hour` (float), `lmp_by_bus` (a list of `{"bus": int, "lmp_dollars_per_MWh": float}` covering every bus, in bus-array order), `reserve_mcp_dollars_per_MWh` (float) and `binding_lines` (list).
- `impact_analysis` contains `cost_reduction_dollars_per_hour`, `buses_with_largest_lmp_drop` (exactly 3 entries) and `congestion_relieved` (a JSON boolean).
- Cast every value to a native Python int, float or bool. numpy types make `json.dump` fail.
- Round to about 2–4 decimals. Compute deltas from unrounded values, then round.

**Step plan.**
1. Run a one-liner to see the keys and sizes, without printing arrays:
   `python3 -c "import json;d=json.load(open('network.json'));print(d.keys(),d['baseMVA'],len(d['bus']),len(d['gen']),len(d['branch']),d['reserve_requirement'],set(int(r[3]) for r in d['gencost']),set(int(r[0]) for r in d['gencost']))"`
2. Check the target line:
   `python3 -c "import json;d=json.load(open('network.json'));print([b[:11] for b in d['branch'] if {int(b[0]),int(b[1])}=={64,1501}])"`
3. Write `solve.py` with a function `solve(branch)` that returns cost, LMPs, MCP, binding lines and flows. Run it for the base case and the counterfactual, then dump `report.json`. Print only the summary: status, both costs, MCPs, number of binding lines, the target line's loading in both cases and the top-3 drops.
4. Confirm `prob.status == "optimal"` in both cases. Run the LMP sign sanity check.
5. Validate the output:
   `python3 -c "import json;r=json.load(open('report.json'));print(r.keys(),len(r['base_case']['lmp_by_bus']),r['impact_analysis'])"`

**Pitfalls.**
- Dense B matrix or Python loops over thousands of buses inside cvxpy expressions make it slow. Use sparse matrices and vector constraints.
- Do not forget c0 in the cost.
- Do not index buses as `num - 1`.
- If CLARABEL complains, try ECOS. Do not use OSQP.
