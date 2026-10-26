## Reference notes

- The input is already a per-second energy profile; no audio extraction or detector CLI is needed. Read the `energies` array from `/root/work/energies.json` with Python’s standard-library `json` module. Element `i` covers `[i, i+1)` seconds.
- Compute the baseline from **exactly** `energies[0:6]`; use twice that mean as the threshold. Keep the unrounded threshold for comparisons, and round it to three decimal places only for JSON output.
- For each index `i`, the trailing average is `sum(energies[max(0, i-2):i+1]) / len(energies[max(0, i-2):i+1])`. The slice’s upper bound is exclusive, so `i+1` includes index `i`.
- Examine candidate indices in ascending order, starting at 6. A candidate needs three available trailing averages—at `i`, `i+1`, and `i+2`—each **strictly** greater than the threshold. Stop at the first qualifying index; do not detect later quiet periods as opening segments.
- Write one JSON object with exactly `method`, `threshold`, `segments`, `total_segments`, and `total_duration_seconds`. Use `method: "trailing_energy_transition"`. A positive end yields one segment `{"start": 0, "end": end, "duration": end}`; otherwise use `[]` and zero totals. `start`, `end`, `duration`, and totals are integers.

```python
import json

with open("/root/work/energies.json") as f:
    energies = json.load(f)["energies"]

# Calculate, then write the required object:
with open("/root/work/initial_silence.json", "w") as f:
    json.dump(output, f)
```
