## Reference notes

Use the local files with Python’s `csv` module or pandas; no download or USGS API is needed.

- **RDB:** Ignore lines starting `#`. The next line is the tab-separated header; skip the immediately following field-type line. Read `site_no` as **text** to retain leading zeroes. `00065` is gage height in **feet**; convert it to numeric so blank heights become missing. `datetime` is local time: use its calendar date without UTC conversion. Ignore quality-code columns.
- **NWS CSV:** Read `usgs id` as text. Each data row has one extra unnamed trailing field; discard it rather than letting it shift the named columns. Convert `action stage` and `flood stage` to numeric feet. A threshold of `-9999`, if present, means undefined.

Compact parsing pattern to adapt:

```python
import csv
import pandas as pd

with open(rdb_path, newline="") as f:
    lines = (line for line in f if not line.startswith("#"))
    columns = next(lines).rstrip("\r\n").split("\t")
    next(lines)  # field-type line
    readings = pd.DataFrame(
        csv.reader(lines, delimiter="\t"), columns=columns
    )

with open(csv_path, newline="") as f:
    reader = csv.reader(f)
    columns = next(reader)
    gauges = pd.DataFrame(
        (row[:len(columns)] for row in reader), columns=columns
    )
```

Filter readings to **July 1–8, 2025 inclusive**, then group by station ID and *local calendar date* and take the maximum available `00065` height. A date with only missing heights cannot cross a threshold. For each station with usable thresholds, the first action/flood dates are the earliest grouped dates where `daily_max >= action stage` and `daily_max >= flood stage`, respectively. Retain only stations with a flood date; action and flood may first occur on the same date. Compute `lead_days` by subtracting the **dates**, not reading timestamps.

Write tab-separated output with `csv.writer(..., delimiter="\t")` or `DataFrame.to_csv(..., sep="\t", index=False)`. Use the four requested columns in order, `YYYY-MM-DD` dates, integer day counts, and rows sorted by the **text** station ID.
