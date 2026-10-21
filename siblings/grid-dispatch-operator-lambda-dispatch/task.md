# Economic Dispatch with System Lambda

`/root/work/network.json` is a MATPOWER-style snapshot with the keys `baseMVA`, `bus`, `gen` and `gencost`.

- Bus column 2 (0-indexed) is PD in MW.
- Gen columns are GEN_BUS, PG, QG, QMAX, QMIN, VG, MBASE, GEN_STATUS, PMAX, PMIN.
- Each gencost row is polynomial type 2 with NCOST = 3: `[2, startup, shutdown, 3, c2, c1, c0]`. The cost is c2*P^2 + c1*P + c0 in $/h, with P in MW.

Compute the lossless economic dispatch with no network constraints:

- Minimize the total cost of the in-service generators (GEN_STATUS = 1).
- Their total output must equal the total system load (sum of PD).
- Each in-service unit must satisfy PMIN <= P <= PMAX.
- Out-of-service generators produce 0 MW and incur no cost.
- The PG column is a stale previous schedule and must not be used.

Write `/root/work/dispatch.json` with this structure:
```json
{
  "generators": [{"id": 1, "bus": 3, "output_MW": 120.5}, ...],
  "system_lambda": 31.234,
  "total_cost": 15234.56,
  "load_MW": 640.2,
  "spinning_margin_MW": 410.7
}
```
The fields are defined as follows:

- `generators`: one entry per gen row, in file order. `id` is the 1-based row index, `bus` is GEN_BUS, and `output_MW` is rounded to 2 decimals.
- `system_lambda`: the system marginal price in $/MWh. This is dC/dP = 2*c2*P + c1 of any unit not at a limit. Round to 3 decimals.
- `total_cost`: total $/h of the in-service units, including c0. Round to 2 decimals.
- `load_MW`: total load, rounded to 2 decimals.
- `spinning_margin_MW`: the sum over in-service units of (PMAX - output), rounded to 2 decimals.
