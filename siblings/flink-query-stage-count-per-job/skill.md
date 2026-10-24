## Reference notes

Use Python’s standard-library `gzip` and `csv`; no PDF or pipeline tooling is needed.

- The `.csv.gz` inputs have **no header**. Read with `gzip.open(path, "rt", newline="")` and `csv.reader(...)`. Relevant zero-based fields are:
  - Job events: `row[2]` job_id, `row[3]` event_type.
  - Task events: `row[0]` timestamp, `row[2]` job_id, `row[5]` event_type.
- Convert IDs, timestamps, and event types to `int`. Job FINISH is type `4`; task SUBMIT is type `0`. Retain every qualifying SUBMIT row, including repeated task indices.
- Timestamps are **microseconds**: the 10-minute threshold is `600 * 1_000_000`. After sorting a job’s SUBMIT timestamps, start a new stage when `current - previous >= threshold`. Compare adjacent SUBMITs, not each timestamp to the stage’s first timestamp.
- Because input rows are unordered, do not sessionize while reading. First collect FINISH job IDs and relevant SUBMIT timestamps, then sort timestamps **within each job**. Sort output job IDs numerically.

Minimal I/O pattern:

```python
import csv
import gzip

with gzip.open(input_path, "rt", newline="") as stream:
    for row in csv.reader(stream):
        # Select needed columns; convert numeric fields with int().
        pass

with open(output_path, "w", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(["job_id", "num_stages", "largest_stage"])
    # Write one integer-valued row per qualifying job.
```

A qualifying job must have both a FINISH job event and at least one task SUBMIT. For each such job, count its stages and track the maximum number of SUBMIT rows in any one stage. After writing, inspect the header and a few rows, and confirm the output IDs are ascending and unique.
