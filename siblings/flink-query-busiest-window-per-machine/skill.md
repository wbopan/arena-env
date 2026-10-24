## Reference notes

- The PDF tools and data-engineering CLIs in the supplied skills are not needed here. Use Python standard-library `gzip`, `csv`, and `json`; the file is a gzipped CSV **without a header**.
- Stream rows rather than loading the whole trace. Relevant zero-based columns are `timestamp=0`, `job_id=2`, `machine_id=4`, and `event_type=5`:
  ```python
  import csv, gzip, json

  with gzip.open("/root/work/data/task_events.csv.gz", "rt", newline="") as f:
      for row in csv.reader(f):
          timestamp, job_id, machine_id, event_type = (
              row[0], row[2], row[4], row[5]
          )
          # filter and aggregate here
  ```
- Retain only event type `1`, timestamps **greater than zero**, and nonempty machine IDs. Parse timestamps as Python `int` to preserve microsecond precision. Use `str(int(machine_id))` for decimal-string JSON keys.
- Event-time window width is `300_000_000` microseconds. Compute `start = (timestamp // width) * width`; the window is `[start, start + width)`. Input row order does not determine the winning window.
- Count events by `(machine_id, start)`. For each machine, choose the largest count, breaking ties by the **smallest** start. `distinct_jobs` is the size of the set of job IDs in that chosen window—not the number of task indices or rows.
- A memory-conscious approach is two streaming passes: count machine/window pairs and select winners in the first; in the second, collect job-ID sets **only** for winning pairs. This avoids keeping job sets for every window.
- Write one JSON object with native Python integer values:
  ```python
  with open("/root/work/busiest_windows.json", "w", encoding="utf-8") as f:
      json.dump(result, f)
  ```
  After running the script, briefly inspect the output: keys should be decimal strings, each value should have the four requested fields, and each `window_end - window_start` should equal the width.
