# DC Power Flow Line Loading

The file `/root/work/network.json` holds a transmission network snapshot in MATPOWER layout. Its keys are `baseMVA`, `bus`, `gen` and `branch`, and the columns follow MATPOWER order:

- bus: BUS_I, BUS_TYPE, PD, QD, ...
- gen: GEN_BUS, PG, QG, QMAX, QMIN, VG, MBASE, GEN_STATUS, PMAX, PMIN
- branch: F_BUS, T_BUS, BR_R, BR_X, BR_B, RATE_A, RATE_B, RATE_C, TAP, SHIFT, BR_STATUS, ANGMIN, ANGMAX

Bus numbers are not contiguous.

Solve a DC power flow for the scheduled dispatch using these conventions:

- Lines are lossless and all voltages are flat at 1.0 pu.
- Each branch has susceptance 1/BR_X. Ignore R, line charging, taps and phase shifts.
- Only in-service branches (BR_STATUS = 1) and in-service generators (GEN_STATUS = 1) participate.
- The net injection at a bus is the sum of PG over the in-service generators at that bus, minus PD.
- The slack bus (BUS_TYPE = 3) has angle 0. Its injection is whatever balances the system, so the PG listed for the slack-bus generator is not used.

Write `/root/work/branch_flows.csv` as follows:

- The header must be exactly `from_bus,to_bus,flow_MW,loading_pct`.
- Write one row per in-service branch, in the same order as the branch table.
- `from_bus` and `to_bus` are the integer bus numbers F_BUS and T_BUS.
- `flow_MW` is the active power flow in MW. It is positive when power flows from F_BUS toward T_BUS.
- `loading_pct` = 100 * |flow_MW| / RATE_A.
- Round `flow_MW` and `loading_pct` to 2 decimals.
