## Reference notes

Use the **local files** with Python’s `csv` module and, optionally, pandas; no data download is needed. USGS parameter `00065` is gage height in feet. NWS `flood stage` is also in feet; `-9999` means no defined threshold.

```python
import csv
import pandas as pd

# RDB: discard # comments, then read the header and skip the field-type row.
with open("/root/work/gage_height_iv.rdb", newline="") as f:
    rows = csv.reader((line for line in f if not line.startswith("#")),
                      delimiter="\t")
    header = next(rows)
    next(rows)  # RDB field types, not an observation
    observations = pd.DataFrame(rows, columns=header)

# NWS CSV: data rows have an extra, unnamed trailing field.
with open("/root/work/nws_gauges.csv", newline="") as f:
    rows = csv.reader(f)
    header = next(rows)
    thresholds = pd.DataFrame(
        (row[:len(header)] for row in rows), columns=header
    )
```

Keep `site_no` and `usgs id` as **text** so leading zeroes survive. Check the RDB header for the `00065` value field; do not select a `00065_cd` quality-code field. Convert heights and `flood stage` with `pd.to_numeric(..., errors="coerce")`; blank heights become missing, and missing daily values cannot establish flooding. Exclude missing and `-9999` thresholds.

Use `datetime`’s displayed calendar date (for example, `datetime_string[:10]`), **without timezone conversion**. Filter dates inclusively from May 10 through May 15, 2025. For each station and date, take the maximum available height, then count dates where `daily_max >= flood_stage`. Include only stations with a positive count; sort by **station ID ascending**, not by count.

For output, `csv.writer` with `newline=""` writes the required header and rows:

```python
writer.writerow(["station_id", "flood_days"])
# writer.writerow([station_id, int(flood_days)])
```
