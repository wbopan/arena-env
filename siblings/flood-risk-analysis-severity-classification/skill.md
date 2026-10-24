### Reference notes

Use the **local files** with Python’s `csv` and `json` modules or pandas; no USGS download is needed. Parameter `00065` is gage height in **feet**. Keep station IDs as strings so leading zeros survive.

```python
import csv
from pathlib import Path
import pandas as pd

work = Path("/root/work")

# RDB: ignore comments, then discard the field-format row after the header.
with (work / "gage_height_iv.rdb").open(newline="") as f:
    rows = (line for line in f if not line.startswith("#"))
    reader = csv.reader(rows, delimiter="\t")
    header = next(reader)
    next(reader)  # RDB field formats, not data
    gages = pd.DataFrame(reader, columns=header)

# NWS CSV: data rows have one extra trailing empty field.
with (work / "nws_thresholds.csv").open(newline="") as f:
    reader = csv.reader(f)
    header = next(reader)
    thresholds = pd.DataFrame((row[:len(header)] for row in reader),
                              columns=header)
```

Convert `00065` and threshold columns with `pd.to_numeric(..., errors="coerce")`. Drop empty/invalid gage heights; treat `-9999` and invalid thresholds as undefined. Retain only stations with gage readings and a **defined flood stage**; do **not** require any flood days. Match IDs as eight-character strings (for example, `str(value).strip().zfill(8)`) and use `state == "MI"` for the Michigan threshold rows.

Parse `datetime` as the supplied **local time**, with no timezone conversion. Restrict readings to April 1–7 inclusive, then group by station ID and calendar date and take the maximum `00065`. For each station, select the largest daily maximum; on ties choose the earliest date. Compare the **unrounded** peak against defined thresholds in this order: major → moderate → flood (`minor`) → action; otherwise `normal`. A day counts as flooded when its daily maximum **≥ flood stage**.

Round `peak_stage_ft` to two decimals for output. Use native Python `float`/`int` values for JSON, format dates as `YYYY-MM-DD`, sort records by `station_id`, and write `{"stations": [...]}` to `/root/work/flood_severity.json`.
