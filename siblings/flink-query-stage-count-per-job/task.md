# Job stages from cluster task events

The inputs use the Google cluster-usage trace (2011) format. They are gzipped CSV files with no header row, and all timestamps are integers in microseconds.

- `/root/work/data/task_events.csv.gz` has these columns: timestamp, missing_info, job_id, task_index, machine_id, event_type, user, scheduling_class, priority, cpu_request, memory_request, disk_request, different_machine_restriction.
- `/root/work/data/job_events.csv.gz` has these columns: timestamp, missing_info, job_id, event_type, user, scheduling_class, job_name, logical_job_name.

Event type codes: 0 SUBMIT, 1 SCHEDULE, 2 EVICT, 3 FAIL, 4 FINISH, 5 KILL, 6 LOST, 7 UPDATE_PENDING, 8 UPDATE_RUNNING. Rows are NOT in time order.

## Task

A job qualifies if it has a FINISH (type 4) job event in the job events file and at least one task SUBMIT (type 0) event.

For each qualifying job, split its task SUBMIT events into stages using event-time session windows with a 10-minute inactivity gap:

1. Order the job's SUBMIT timestamps.
2. Start a new stage whenever the time since the previous SUBMIT of the same job is 600 seconds or more.
3. Count every SUBMIT row as one task. If the same task index is submitted again, each submission counts separately.

## Output

Write `/root/work/stages.csv` with the header line `job_id,num_stages,largest_stage`.

- Write one row per qualifying job, sorted by job_id ascending.
- All values are plain integers.
- `num_stages` is the number of stages of the job.
- `largest_stage` is the number of SUBMIT events in the job's biggest stage.
- Jobs without a FINISH job event must not appear.
