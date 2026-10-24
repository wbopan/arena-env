## Reference notes

- Use `pandas` for the CSV inputs and Python’s `csv` module for the report. Inspect `spec.yaml` before writing its parser: the standard library has **no YAML parser**, so parse only the structure actually present rather than assuming a particular nesting pattern. Keep the spec’s numeric text for output if it must be copied verbatim; convert values to `float` for calculations.
- Read IDs as strings to preserve their spelling, then sort runs lexicographically by `run_id`. Sort each sensor’s samples by numeric `time_s`. Ignore consecutive pairs with `dt <= 0`.

```python
runs = pd.read_csv("mes_log.csv", dtype={"run_id": str, "alloy": str})
samples = pd.read_csv(
    "thermocouples.csv", dtype={"run_id": str, "tc_id": str}
)
samples["time_s"] = pd.to_numeric(samples["time_s"])
samples["temp_c"] = pd.to_numeric(samples["temp_c"])
```

For one sensor, sum the duration **strictly above** its alloy’s liquidus. Linear interpolation locates a threshold crossing; a sample exactly at liquidus contributes no positive-duration time by itself.

```python
def tal_seconds(sensor, liquidus):
    g = sensor.sort_values("time_s", kind="mergesort")
    pairs = zip(g[["time_s", "temp_c"]].to_numpy()[:-1],
                g[["time_s", "temp_c"]].to_numpy()[1:])
    total = 0.0
    for (t0, y0), (t1, y1) in pairs:
        if t1 <= t0:
            continue
        if y0 > liquidus and y1 > liquidus:
            total += t1 - t0
        elif (y0 <= liquidus < y1) or (y1 <= liquidus < y0):
            crossing = t0 + (liquidus - y0) * (t1 - t0) / (y1 - y0)
            total += (t1 - crossing) if y1 > liquidus else (crossing - t0)
    return total
```

For each MES run, calculate every available sensor’s **unrounded** TAL and select with `min(sensor_results, key=lambda item: (item.tal, item.tc_id))`. Round only the selected TAL to two decimals **before** comparing it inclusively with the alloy’s `tal_min_s` and `tal_max_s`; format its CSV field with two decimal places. A run without sensor rows gets empty `tc_id` and `tal_s` fields and `non-compliant` status.

Create `/root/work/output` if necessary. Write exactly the requested header and one row per MES run in sorted order. After writing, inspect the header, row count, ordering, blank fields, and a few interpolated TAL values.
