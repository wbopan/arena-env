1. Inspect `/root/network.json` cheaply: top-level keys, one thermal generator (limits, ramps, SU/SD, min up/down, t0 fields, piecewise_production, startup tiers) and one renewable.
2. Write one script that builds a UC MILP with scipy `milp` (HiGHS) using above-min production: transitions, t0 obligations, min up/down windows, `p+r <= cap*u - (pmax-SU)v - (pmax-SD)w[t+1]`, ramps on p+r, system balance with curtailable renewables, and reserve from online thermals only.
3. Model cost as convex piecewise segments plus `c0*u` and tiered startup costs via delta binaries.
4. Extract actual MW (pmin*u + p), independently validate everything, and recompute cost; take `reported_mip_gap` from `res.mip_gap` (null if unavailable).
5. Write `/root/report.json` in the exact schema (input order, hours start at 1, all checks "pass"), then reload it to verify lengths and the summary.
