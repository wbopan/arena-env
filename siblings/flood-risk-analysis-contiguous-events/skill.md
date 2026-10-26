## Reference notes

Use local files; no download library or network call is needed. Python’s `csv` and `json` modules suffice; pandas is optional for daily aggregation.

```python
import csv

# RDB: remove comment lines before reading the tab-separated table.
with open(rdb_path, newline="") as f:
    rows = csv.reader((line for line in f if not line.startswith("#")),
                      delimiter="\t")
    columns = next(rows)
    next(rows)  # field-type line, not an observation
    observations = csv.DictReader([], fieldnames=columns)  # or zip(columns, row) below
    for row in rows:
        record = dict(zip(columns, row))
        # Process record here.
```

Keep `site_no` and NWS `usgs id` as **strings** so leading zeroes survive. In the RDB table, `00065` is the height in feet; `00065_cd` (if present) is not a height. Ignore empty `00065` values. Interpret `datetime` by its **local calendar date**, without converting time zones.

```python
with open(nws_path, newline="") as f:
    reader = csv.reader(f)
    headers = next(reader)
    for row in reader:
        record = dict(zip(headers, row[:len(headers)]))
        # The extra unnamed trailing field is discarded.
```

Convert `flood stage` to a number before comparison. An empty threshold or `-9999` denotes no usable flood threshold. Match IDs exactly after any surrounding whitespace is stripped; do not convert them to integers.

For each `(station_id, date)` within June 1–9, retain the **maximum of usable instantaneous heights**. A flood date satisfies `daily_max >= flood_stage` (equality counts). Group flood dates into an event only when their calendar dates differ by exactly one day; a date without usable observations must break the group. An event’s peak is the maximum of its flood-day daily maxima, and its inclusive duration is the count of its flood dates.

Write a JSON **array**, not a wrapper object. Include only stations with events; sort records by the string `station_id`, then ISO-format `start_date`. Each record has exactly the five requested keys, with `duration_days` as an integer and `peak_ft` as a numeric value rounded to two decimal places.
