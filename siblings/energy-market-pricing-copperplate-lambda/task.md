The market team wants a copper-plate economic dispatch, with no transmission constraints, as a benchmark for the system marginal price.

The input is `/root/work/network.json`, in MATPOWER-style JSON. It contains:
- `bus`: column 0 = bus number, column 2 = Pd in MW
- `gen`: column 0 = bus number, column 7 = status (1 = online), column 8 = PMAX in MW, column 9 = PMIN in MW
- `gencost`: one row per `gen` row, polynomial model 2 with NCOST = 3. Columns 4, 5 and 6 are c2, c1 and c0, and the cost is c2*P^2 + c1*P + c0 in $/hr, with P in MW.

Dispatch only the generators with status 1. Each online generator must produce between its PMIN and PMAX. Offline generators produce nothing and are excluded from the output. Total generation must equal total system load, which is the sum of Pd over all buses. Minimize total cost.

Write `/root/work/dispatch.json`:
```json
{"total_load_MW": 0.0,
 "system_lambda_dollars_per_MWh": 0.0,
 "total_cost_dollars_per_hour": 0.0,
 "generators": [{"gen_index": 1, "bus": 17, "output_MW": 120.5, "at_limit": "none"}]}
```

Field definitions:
- `system_lambda_dollars_per_MWh`: the marginal cost of serving one extra MW of system load at the optimum.
- `total_cost_dollars_per_hour`: includes c0 of every online generator.
- `generators`: online generators only, listed in `gen`-array order.
  - `gen_index`: the 1-based row number in the `gen` array, counting offline rows.
  - `at_limit`: "pmax" or "pmin" if the output is within 0.01 MW of that limit, otherwise "none".

Round MW values to 3 decimals and dollar values to 4 decimals.
