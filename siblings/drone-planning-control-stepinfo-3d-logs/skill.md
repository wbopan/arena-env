## Reference notes

Use Python’s standard-library `csv`, `json`, and `math` modules; no simulator or controller code is needed. The relevant 3D step-response definition uses **Euclidean distance to the fixed target**, not separate axis errors.

```python
import csv, json, math
from collections import defaultdict

with open('/root/work/targets.json') as f:
    targets = json.load(f)  # keys are flight-id strings; values are [x, y, z]

flights = defaultdict(list)
with open('/root/work/flights.csv', newline='') as f:
    for row in csv.DictReader(f):
        flights[row['flight_id']].append((
            float(row['t']),
            (float(row['x']), float(row['y']), float(row['z']))
        ))

# For each flight, sort samples by numeric time before calculating distances:
samples = sorted(flights[flight_id], key=lambda sample: sample[0])
dist = [
    math.dist(position, target)
    for time, position in samples
]
```

For each sorted flight, let `d0 = dist[0]` and retain the **logged** times (no interpolation):

- If `d0 < 1e-6`, all four metrics are `0.0`.
- `RiseTime`: time of the first `d <= 0.1*d0`; Python `None` becomes JSON `null` if absent.
- `SettlingTime`: time of the **last** `d > 0.02*d0`; `0.0` if none. Equality is inside the band.
- `Overshoot_pct`: find the first index with `d <= 0.02*d0`; use `100 * max(dist[index:]) / d0`. If there is no such index, use `0.0`.
- `SteadyStateError`: `dist[-1]`, in metres.

Build the output keyed by the strings from `targets.json`, with exactly `RiseTime`, `SettlingTime`, `Overshoot_pct`, and `SteadyStateError` in each value. Round numeric metrics to four decimals while preserving `None`; write with `json.dump(...)` to `/root/work/step_metrics.json`. Inspect the CSV header and a few rows cheaply, write one script, run it, then inspect the resulting JSON for the expected ids and keys.
