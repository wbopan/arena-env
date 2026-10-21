1. Inspect `network.json` only via python one-liners: keys, sizes, baseMVA, gencost types, reserve fields and the 64–1501 branch row(s).
2. Write one cvxpy script (sparse DC-OPF in MW: Pg, Rg, theta; Pg+Rg ≤ Pmax; Rg ≤ reserve_capacity; ΣRg ≥ requirement; ±RATE_A limits; slack θ=0) and solve it with CLARABEL twice, the second time with the 64–1501 RATE_A ×1.2.
3. Take LMPs from the nodal balance duals (sign-check them against marginal cost) and the reserve MCP from the reserve dual; binding lines are those with loading ≥ 99%.
4. Write `report.json` with the exact schema: top-3 most negative deltas, cost_reduction = base − cf, congestion_relieved = target line not binding in the counterfactual.
5. Reload the file to check its keys and types.
