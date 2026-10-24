## Reference notes

Use `pandas` for the CSV and `yaml.safe_load` for the configuration. Blank `lead_speed` and `distance` cells become missing values; use `.notna()` rather than comparing them to empty strings.

```python
import json
import pandas as pd
import yaml

with open('/root/work/sim_config.yaml') as f:
    cfg = yaml.safe_load(f)

settings = cfg['acc_settings']
dt = cfg['simulation']['dt']
df = pd.read_csv('/root/work/drive_log.csv')

lead_mask = df['lead_speed'].notna()
first_lead = lead_mask.to_numpy().nonzero()[0][0]
cruise = df.iloc[:first_lead]       # Stop BEFORE first detected lead
lead = df.loc[lead_mask]            # Include every lead row
```

If checking for an empty lead mask, do so *before* indexing the first position. Use row order, not a time threshold, to define the cruise segment.

- Rise time: in `cruise`, select the **first** `time` meeting each of `ego_speed >= 0.1 * set_speed` and `>= 0.9 * set_speed`; subtract the former from the latter. Do not interpolate.
- Overshoot: `max(0, (cruise['ego_speed'].max() - set_speed) / set_speed * 100)`.
- Speed steady-state error: `abs(set_speed - cruise['ego_speed'].tail(25).mean())`.
- Desired following distance is `min_distance + time_headway * ego_speed`. Compute the mean of **actual minus desired** distance over `df.tail(50)` (the last 50 file rows), then take its absolute value.
- Minimum distance: `lead['distance'].min()`.
- TTC: restrict `lead` to rows with `ego_speed > lead_speed`; compute `distance / (ego_speed - lead_speed)` and take the minimum. Use Python `None` if that subset is empty.
- Follow duration: `len(lead) * dt`.

Write one JSON object with exactly the seven requested keys. Convert pandas/NumPy scalar results to Python `float` before `round(value, 3)`; leave `None` unchanged so it becomes JSON `null`. The standard-library writer is `json.dump(result, f, allow_nan=False)`.
