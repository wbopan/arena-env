## Reference notes

Use Python’s `json`, `csv`, and `numpy`. Parse the JSON directly rather than printing the network file; a cheap first inspection is the array lengths and `baseMVA`. The task uses only `baseMVA`, `bus`, `gen`, and `branch`.

MATPOWER columns are **0-indexed** in Python:

| Table | Fields needed |
|---|---|
| `bus` | bus number `[0]`, type `[1]` (`3` = slack), demand PD `[2]` in MW |
| `gen` | bus number `[0]`, scheduled PG `[1]` in MW, status `[7]` |
| `branch` | F_BUS `[0]`, T_BUS `[1]`, reactance X `[3]`, RATE_A `[5]`, status `[10]` |

Bus IDs need not be contiguous: use `{int(bus[0]): row_index for row_index, bus in enumerate(buses)}` for **both** generator and branch endpoints. Never use `bus_id - 1`.

For each in-service branch, set `b = 1.0 / branch[3]` and add its contributions to the nodal matrix:

```python
B[f, f] += b
B[t, t] += b
B[f, t] -= b
B[t, f] -= b
```

Form each bus’s scheduled net injection as `(sum of in-service PG at that bus − PD) / baseMVA`. Find the bus with `BUS_TYPE == 3`; fix its angle to zero and **do not use its scheduled PG to constrain the solve**. Solve only the non-slack rows and columns:

```python
keep = [i for i in range(len(buses)) if i != slack_idx]
theta = np.zeros(len(buses))
theta[keep] = np.linalg.solve(B[np.ix_(keep, keep)], injection[keep])
```

For each in-service branch **in original table order**:

```python
flow_MW = (theta[f] - theta[t]) / branch[3] * baseMVA
loading_pct = 100 * abs(flow_MW) / branch[5]
```

The flow sign is positive from F_BUS to T_BUS. Ignore resistance, charging, taps, and phase shifts. Write CSV with `csv.writer`, the exact header `from_bus,to_bus,flow_MW,loading_pct`, integer endpoint IDs, and two-decimal flow/loading fields (for example, `f"{flow_MW:.2f}"`). Check the row count against the number of in-service branches and inspect the header and a few output rows.
