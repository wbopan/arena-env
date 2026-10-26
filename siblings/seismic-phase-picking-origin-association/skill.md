## Reference notes

Use Python’s standard-library `csv` and `json`; waveform readers, phase-picking models, and data-center clients are unnecessary because the inputs are already candidate indices.

```python
import csv
import json

with open("/root/work/stations.csv", newline="") as f:
    stations = list(csv.DictReader(f))
with open("/root/work/candidates.csv", newline="") as f:
    candidates = list(csv.DictReader(f))
```

`DictReader` returns strings: convert `distance_km` to a number and `pick_idx` to `int`. Group candidate indices by `(station, phase)` so each prediction is compared only with its corresponding station-phase candidates.

At sampling interval \(\Delta t=0.1\) s, predicted arrival index is
\[
o+\frac{d/v}{\Delta t},
\]
where \(o\) is the origin index, \(d\) is distance in km, and \(v\) is 6 km/s for P or 3 km/s for S. The supplied distances make these indices integral; avoid accumulating floating-point error when converting them to integers.

For a prediction `pred` and its candidate-index list, `min(indices, key=lambda i: (abs(i - pred), i))` implements the required pick tie-break. Sum `abs(chosen - pred)` over **every** station-phase pair for each `o` in `range(61)`. Compare origins by `(total_residual, origin_idx)` to favor the smaller origin on a tie. Sort output picks by `(station, phase)` (P precedes S), and write one JSON object with native Python `int` values using `json.dump(..., f)`.
