## Reference notes

Use Python’s standard-library `csv` module. These are ordinary CSV tables, not ObsPy waveform files; GaMMA association and ML phase pickers are unnecessary because the picking rule is specified directly.

```python
import csv

with open("/root/work/stations.csv", newline="") as f:
    stations = list(csv.DictReader(f))
with open("/root/work/waveforms.csv", newline="") as f:
    waveforms = list(csv.DictReader(f))
```

`DictReader` values are strings: keep `station_id` as a string, convert `response` and `counts` to numbers, and convert `sample` with `int()`. For each row, normalized amplitude is `abs(counts) / response`; compare the **unrounded** result with `>= 3`.

Process each `(station_id, channel)` trace independently, in numeric `sample` order. A run contains qualifying samples at consecutive integer sample times (`next_sample == previous_sample + 1`); a below-threshold sample or a time gap ends it. For each run of at least two samples, use its first sample as `time_s` and its maximum normalized amplitude as `peak_unit`. Map `Z` to lowercase `p`, `E` to lowercase `s`.

Sort picks by `(numeric time_s, station_id, phase)` before writing. Use `csv.DictWriter` with `fieldnames=["station_id", "phase", "time_s", "peak_unit"]`, `writeheader()`, and exactly those fields. Format the peak to two decimal places only when writing (for example, `f"{peak:.2f}"`); write the time as an integer.
