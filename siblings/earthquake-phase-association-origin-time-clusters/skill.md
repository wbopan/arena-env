## Reference notes

Use Python’s standard-library `csv` and `math`; this is a fixed-source calculation, not a GaMMA association problem. GaMMA expects timestamped picks and estimates source parameters, whereas these inputs have numeric seconds and a specified source.

```python
import csv
import math

with open("/root/work/stations.csv", newline="") as f:
    stations = list(csv.DictReader(f))
with open("/root/work/picks.csv", newline="") as f:
    picks = list(csv.DictReader(f))
```

`DictReader` values are strings: convert coordinates, `time_s`, and `prob` with `float()`. Match `station_id` between the two files as a string. For station coordinates `(x_km, y_km, 0)`, straight-line distance from the source is

`d_km = math.sqrt((x_km - 9)**2 + y_km**2 + 6**2)`.

Travel time is `d_km / 6` for P or `d_km / 3` for S; inferred origin time is `pick_time_s - travel_time`. These are elapsed seconds, not timestamps. Exclude `prob < 0.8` **before** clustering or counting.

Sort inferred times. Start a new cluster only when the gap from the **immediately preceding** sorted estimate exceeds `0.30` seconds. Thus a chain of qualifying adjacent gaps remains one cluster even if its first and last times differ by more than `0.30`. For each cluster, count all included picks, distinct station IDs, and P picks separately; retain it only with at least three distinct stations and two P picks. Take the arithmetic mean of the cluster’s *unrounded* inferred times, then round the mean to three decimal places.

Write CSV with `newline=""`, header `time_s,n_picks,n_stations`, and retained rows ordered by origin time. Format the mean with `f"{mean:.3f}"` if three decimal digits should be visible. An empty result still needs the header.
