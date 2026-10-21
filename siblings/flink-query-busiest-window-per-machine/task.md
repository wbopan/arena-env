# Busiest scheduling window per machine

The input is `/root/work/data/task_events.csv.gz`, in the Google cluster-usage trace (2011) task-event format. It is gzipped CSV with no header row, and timestamps are integers in microseconds.

Columns: timestamp, missing_info, job_id, task_index, machine_id, event_type, user, scheduling_class, priority, cpu_request, memory_request, disk_request, different_machine_restriction.

Event type codes: 0 SUBMIT, 1 SCHEDULE, 2 EVICT, 3 FAIL, 4 FINISH, 5 KILL, 6 LOST, 7 UPDATE_PENDING, 8 UPDATE_RUNNING. Rows are not in time order.

Trace conventions:
- A timestamp of 0 means the event happened before the trace window. Such events must be excluded.
- Rows with an empty machine_id are not tied to a machine. Ignore them.

## Task

Consider only SCHEDULE (type 1) events. Assign each event to an event-time tumbling window of 5 minutes (300,000,000 us) aligned to timestamp 0. The window start is `floor(timestamp / 300000000) * 300000000`.

For every machine that has at least one valid SCHEDULE event:
1. Find the window with the most SCHEDULE events on that machine.
2. If several windows tie, take the earliest one.

## Output

Write `/root/work/busiest_windows.json`. It must be a single JSON object keyed by machine_id, written as a decimal string. Each value is an object with these integer fields:

- `window_start`: start of the window, in microseconds.
- `window_end`: `window_start + 300000000`.
- `schedule_count`: number of SCHEDULE events of that machine in the window.
- `distinct_jobs`: number of distinct job_ids among those events.
