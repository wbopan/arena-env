**Inputs and libraries**
- `network.json` is MATPOWER data stored as JSON. It can be very large, so never `cat`, `head` or `sed` it. Load it with `json.load` in Python.
- Keys: `baseMVA`, `bus`, `gen`, `branch`, `gencost`, `reserve_capacity` (MW per generator, r̄), and `reserve_requirement` (MW, the system total R).
- Use `numpy`, `scipy.sparse` and `cvxpy` with the CLARABEL solver. Check that they import first: `python3 -c "import cvxpy,scipy;print(cvxpy.installed_solvers())"`.

**Column conventions (0-indexed)**
- bus: `[0]` bus number, `[1]` type (3 = slack), `[2]` Pd in MW.
- gen: `[0]` bus number, `[7]` status, `[8]` PMAX in MW, `[9]` PMIN in MW.
- branch: `[0]` from bus, `[1]` to bus, `[3]` reactance X in pu, `[5]` RATE_A in MVA (0 means unlimited, so skip the limit), `[10]` status (only branches with status 1 are in service).
- gencost (model 2, polynomial): `[3]` NCOST, then coefficients from highest order down.
  - NCOST=3: `[4],[5],[6]` are c2, c1, c0.
  - NCOST=2: `[4],[5]` are c1, c0.
  - Cost = c2·P² + c1·P + c0 in $/hr, with P in MW.
  - Include c0 for every generator in the total cost.
- Bus numbers may be non-contiguous. Always build `idx = {int(b[0]): i for i, b in enumerate(bus)}` and never use `bus - 1`.

**Model (DC-OPF with reserve co-optimisation)**
- Variables: `Pg` (MW, n_gen) and `Rg` (MW, n_gen), plus `theta` (rad, n_bus).
- Objective: minimise Σ cost(Pg).
- Constraints:
  1. `PMIN ≤ Pg ≤ PMAX`.
  2. `Rg ≥ 0` and `Rg ≤ reserve_capacity`.
  3. `Pg + Rg ≤ PMAX` (the standard capacity coupling).
  4. `sum(Rg) ≥ reserve_requirement`.
  5. Nodal balance, all in pu: `Cg @ Pg/baseMVA − Pd/baseMVA == B @ theta`.
  6. `theta[slack] == 0`.
  7. For each rated, in-service branch: `|b·(θf−θt)·baseMVA| ≤ RATE_A`, where b = 1/x.
- If a generator has status 0, force `Pg = Rg = 0` for it, but still list it in the output.
- B is built from in-service branches with x ≠ 0, as in the skill: `B[f,f]+=b, B[t,t]+=b, B[f,t]-=b, B[t,f]-=b`.

**Vectorised build (fast for large cases)**

```python
import json, numpy as np, scipy.sparse as sp, cvxpy as cp
d=json.load(open('network.json')); base=d['baseMVA']
bus=np.array(d['bus']); gen=np.array(d['gen']); br=np.array(d['branch']); gc=np.array(d['gencost'])
nb,ng=len(bus),len(gen); idx={int(b[0]):i for i,b in enumerate(bus)}
br=br[(br[:,10]==1)&(br[:,3]!=0)]
f=np.array([idx[int(x)] for x in br[:,0]]); t=np.array([idx[int(x)] for x in br[:,1]])
b=1/br[:,3]; nl=len(br)
A=sp.csr_matrix((np.r_[np.ones(nl),-np.ones(nl)],(np.r_[np.arange(nl)]*2 if False else np.r_[np.arange(nl),np.arange(nl)],np.r_[f,t])),(nl,nb))
Bf=sp.diags(b)@A; B=A.T@Bf
Cg=sp.csr_matrix((np.ones(ng),([idx[int(x)] for x in gen[:,0]],np.arange(ng))),(nb,ng))
Pd=bus[:,2]; slack=int(np.where(bus[:,1]==3)[0][0])
Pg=cp.Variable(ng); Rg=cp.Variable(ng); th=cp.Variable(nb)
```

The cost uses the NCOST-dependent coefficient columns, as a vector of c2, c1 and c0:

```python
c2=np.where(gc[:,3]>=3,gc[:,4],0); c1=np.where(gc[:,3]>=3,gc[:,5],gc[:,4]); c0=np.where(gc[:,3]>=3,gc[:,6],gc[:,5])
cost=c2@cp.square(Pg)+c1@Pg+c0.sum()
```

The line-limit rows use `rated = br[:,5]>0`: `flow = Bf@th*base`, with `flow[rated] <= rate` and `>= -rate`.

Solve with `prob.solve(solver=cp.CLARABEL)` and check that `prob.status` is `optimal`. If the quadratic form causes trouble, write `cp.sum(cp.multiply(c2, cp.square(Pg)))`.

**Post-processing**
- Line flows in MW are `Bf@theta.value*base`.
- `loading_pct = |flow| / RATE_A * 100`, computed only for branches with RATE_A > 0.
- Sort descending and keep the top 3. Report the original bus numbers: `{"from": int(br[k,0]), "to": int(br[k,1]), "loading_pct": round(.,2)}`.
- `operating_margin_MW = Σ(PMAX − Pg − Rg)` over all generators.
- Totals:
  - `cost_dollars_per_hour` is the objective value, including c0.
  - `load_MW` is Σ Pd.
  - `generation_MW` is Σ Pg, which should equal the load because DC is lossless.
  - `reserve_MW` is Σ Rg.
- Round values to 2 decimals. Cast everything to Python float/int so JSON serialisation works.

**Output: `report.json`** (working dir, same location as network.json unless the task says otherwise)

```json
{"generator_dispatch":[{"id":1,"bus":<gen bus no>,"output_MW":..,"reserve_MW":..,"pmax_MW":..},...],
 "totals":{"cost_dollars_per_hour":..,"load_MW":..,"generation_MW":..,"reserve_MW":..},
 "most_loaded_lines":[{"from":..,"to":..,"loading_pct":..}, x3],
 "operating_margin_MW":..}
```

`id` is the 1-based generator order in the file. List every generator.

**Plan**
1. Check the file size with `ls -la; du -h network.json`. Print a key summary with a Python one-liner: the keys, the bus/gen/branch counts, total load, `reserve_requirement`, sum of `reserve_capacity`, the set of gencost NCOST values, the count of RATE_A=0 branches, and the count of out-of-service branches/generators.
2. Write `solve.py` using the build above and run it.
3. Verify these properties:
   - The status is optimal.
   - |Σ Pg − load| < 1e-3.
   - Σ Rg ≥ R.
   - Pg + Rg ≤ Pmax + 1e-6 for every generator.
   - Max loading ≤ 100.01%.
   - The JSON keys and types match the structure exactly.
   - There are exactly 3 lines, sorted descending.
4. Print only the totals and top lines, not the full dispatch list.

**Pitfalls**
- Do not use `bus - 1` indexing.
- Do not forget c0.
- Reserves are already in MW, so do not scale them by baseMVA.
- Skip branches with zero rating when computing limits and loading.
- Drop out-of-service branches.
- Avoid OSQP; use CLARABEL.
