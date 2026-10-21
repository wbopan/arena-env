The day-ahead dispatch for tomorrow's peak hour is fixed. The operations desk needs the transmission flows and line loadings that this schedule produces.

The network snapshot is `/root/work/network.json`, in MATPOWER-style JSON. It contains:
- `baseMVA`
- `bus`: column 0 = bus number, column 1 = bus type (3 = slack), column 2 = Pd in MW
- `gen`: column 0 = bus number, column 1 = scheduled output PG in MW, column 7 = status (1 = in service)
- `branch`: column 0 = from bus, column 1 = to bus, column 3 = series reactance x in per-unit, column 5 = RATE_A in MW, column 10 = status (1 = in service)

Bus numbers are not contiguous.

Run a DC power flow for this schedule. Use the standard DC assumptions: lossless lines, flat 1.0 pu voltages, small angles, and slack bus angle = 0. Ignore resistance, line charging, taps, and out-of-service branches. The net injection at a bus is the sum of PG of the in-service generators at that bus minus the bus Pd.

Write `/root/work/branch_flows.csv` with the header `from_bus,to_bus,flow_MW,loading_pct`. Write one row per in-service branch, in the same order as the branches appear in the `branch` array.
- `from_bus` and `to_bus`: bus numbers as integers.
- `flow_MW`: real power flow from the from-bus toward the to-bus, in MW. It is negative when power flows the other way.
- `loading_pct`: |flow_MW| / RATE_A x 100.

Round `flow_MW` and `loading_pct` to 2 decimals.
