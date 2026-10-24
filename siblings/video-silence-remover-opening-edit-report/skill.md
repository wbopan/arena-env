## Reference notes

Use Python’s standard-library `json` and `statistics.median`. The inputs are already analysed; no audio, video, detector, or report-generator CLI is needed.

```python
import json
from statistics import median

with open("/root/work/energies.json") as f:
    energies = json.load(f)["energies"]
with open("/root/work/pauses.json") as f:
    pauses = json.load(f)["segments"]

D = len(energies)  # Do not substitute total_seconds or a video duration.
```

- Baseline is `median(energies[:20])`. Search candidate indices in `range(D - 2)`; require **each** of the three consecutive values to be strictly `> 3 * baseline`. Use the first match. If none matches, the opening end is `0`; add `[0, opening_end)` only when non-empty.
- Treat segments as half-open `[start, end)`. Read pause `start` and `end`; do **not** rely on their supplied `duration` or order.
- Clip each endpoint to `[0, D]` (for example, `min(D, max(0, value))`), then discard segments with `end <= start`. Sort by start. While merging, a next `start <= current_end` extends the current segment to `max(current_end, next_end)`. Recompute each merged `duration` as `end - start`.
- Sum **merged** durations, not input durations. Compressed duration is `D - removed`; percentage is `round(removed / D * 100, 2)` when `D > 0`. Handle an empty energy list without calling `median` or dividing by zero.
- Write the task’s exact report keys with `json.dump(...)` to `/root/work/compression_report.json`. `segments_removed` should contain only `start`, `end`, and recomputed `duration`; no detector metadata or segment types.

Short workflow: inspect the two JSON shapes cheaply, write one Python script for detection → clipping/merging → report, run it, then inspect the resulting JSON for sorted non-touching segments and consistent duration totals.
