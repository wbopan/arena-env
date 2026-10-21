1. Inspect `network.json` only through a Python `json.load` summary: counts, load, reserve_requirement, NCOST values, rate-0 and out-of-service branches.
2. Write `solve.py`: a cvxpy DC-OPF (CLARABEL) with sparse B, nodal balance, slack θ=0 and line limits on RATE_A>0, plus reserves (0≤Rg≤r̄, Pg+Rg≤Pmax, ΣRg≥R).
3. Output `report.json` with per-generator output/reserve/pmax, totals (cost incl. c0, load, gen, reserve), the top-3 |flow|/RATE_A lines by bus number, and margin = Σ(Pmax−Pg−Rg).
4. Verify optimal status, gen = load, reserve ≥ R, loadings ≤ 100%, and the exact JSON keys.
