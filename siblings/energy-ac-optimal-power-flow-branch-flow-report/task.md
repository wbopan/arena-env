# Branch Flow Report for a Solved AC Operating Point

The file `/root/work/network.json` holds a small MATPOWER-style case with keys `baseMVA`, `bus` and `branch`. A solved AC operating point is already stored in the bus rows.

Bus rows use the standard 13 columns: `[BUS_I, TYPE, PD, QD, GS, BS, AREA, VM, VA, BASE_KV, ZONE, VMAX, VMIN]`. VM is in per-unit and VA is in degrees. Bus numbers are not contiguous.

Branch rows use the standard 13 columns: `[F_BUS, T_BUS, BR_R, BR_X, BR_B, RATE_A, RATE_B, RATE_C, TAP, SHIFT, BR_STATUS, ANGMIN, ANGMAX]`.

Compute the AC branch flows using MATPOWER's standard pi-model conventions:
- The series admittance is y = 1/(r + jx).
- BR_B is the total charging susceptance, with half placed at each end.
- An ideal transformer with complex ratio N = TAP·e^{j·SHIFT} sits at the from side. TAP = 0 means a ratio of 1. SHIFT is given in degrees.
- S_from is the complex power leaving the from bus into the branch. S_to is the complex power leaving the to bus into the branch.

Write `/root/work/branch_flows.csv`:
- Include one row per in-service branch (BR_STATUS = 1), in input order.
- Skip out-of-service branches.
- Use this exact header: `from_bus,to_bus,p_from_MW,q_from_MVAr,p_to_MW,q_to_MVAr,loss_MW,loading_pct`

Column definitions:
- Powers are in MW / MVAr (per-unit × baseMVA).
- `loss_MW = p_from_MW + p_to_MW`.
- `loading_pct = 100·max(|S_from|, |S_to|)/RATE_A` in MVA. Use 0 when RATE_A = 0.
- `from_bus` and `to_bus` are integer bus numbers.
- Round all other values to 4 decimals.
