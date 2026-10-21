**Goal recap (format only).** Implement `/app/workspace/src/main/java/clusterdata/query/LongestSessionPerJob.java`. Keep the class name, keep extending `AppBase`, and do not touch `pom.xml`. Also create task-event and job-event datatype classes in `clusterdata.datatypes`, using the names that `AppBase` references. Parameters are `--task_input <gz>`, `--job_input <gz>` and `--output <file>`. The output is a local file with one line per job, formatted exactly `(jobId,count)`, for example `(6251812952,37)`. Line order does not matter.

**1. Inspect cheaply (do not cat whole files).**
- `ls /app/workspace/data /app/workspace/data/*/ | head`
- `wc -l /app/workspace/src/main/java/clusterdata/utils/AppBase.java`, then `grep -n "import\|class\|static\|Source\|datatypes" AppBase.java`. This tells you which class names `AppBase` expects (e.g. `TaskEvent`, `JobEvent`), whether it provides sources or helpers, and which methods are required, such as a `fromString` parser.
- `cat LongestSessionPerJob.java`. The skeleton is small. Note how it reads params (`ParameterTool`?) and the env setup.
- `grep -n "flink\|<version>\|mainClass\|finalName" pom.xml | head -20`. This gives the Flink version, which decides the API: `WatermarkStrategy` and `Time.minutes` vs `Duration`. It also gives the jar name.
- `ls src/main/java/clusterdata/*/` to see existing classes.
- Schema: run `pdftotext -layout data/format.pdf - | grep -n -i -A25 "task events table"` and the same for "job events". Use `grep -n -i "event type\|SUBMIT\|FINISH" data/ClusterData2011_2.md | head`.
- Data: `zcat data/task_events/part-00001-of-00500.csv.gz | head -3`, `zcat ... | wc -l`, and `zcat data/job_events/... | head -3`.

**2. Schema facts (Google cluster trace 2011, CSV with no header, empty fields allowed).**

Task events, 13 columns:

| Index | Field |
|---|---|
| 0 | timestamp (µs) |
| 1 | missing info |
| 2 | job ID |
| 3 | task index |
| 4 | machine ID |
| 5 | event type |
| 6 | user |
| 7 | scheduling class |
| 8 | priority |
| 9 | CPU request |
| 10 | memory request |
| 11 | disk request |
| 12 | different-machines restriction |

Job events, 8 columns:

| Index | Field |
|---|---|
| 0 | timestamp (µs) |
| 1 | missing info |
| 2 | job ID |
| 3 | event type |
| 4 | user |
| 5 | scheduling class |
| 6 | job name |
| 7 | logical job name |

Event types: 0 = SUBMIT, 1 = SCHEDULE, 2 = EVICT, 3 = FAIL, 4 = FINISH, 5 = KILL, 6 = LOST, 7 = UPDATE_PENDING, 8 = UPDATE_RUNNING. Confirm these against the PDF.

**Parsing pitfalls.**
- Use `line.split(",", -1)` so trailing empty fields are kept.
- Parse empty numeric fields as 0 or -1 and never throw.
- Use `long` for timestamps and job IDs, and `double` for resource requests.
- Timestamp 0 means "before trace start", which is valid.

**3. Semantics to implement.**
- Keep only task events with event type 0 (SUBMIT). Every SUBMIT row counts as one task, so resubmissions of the same task index count again. Do not dedupe by task index.
- A stage is an event-time session per jobId with a 10-minute gap: 10 min = 600,000,000 µs = 600,000 ms.
- Flink timestamps are milliseconds, so assign `ts/1000` as the event timestamp and use `Time.minutes(10)` / `Duration.ofMinutes(10)`. Alternatively, keep µs and use a gap of 600,000,000. Never mix the two.
- Per job, take the max session count. Emit it once the job has finished, meaning a job event with type 4 (FINISH) for that jobId.

**4. Suggested Flink pipeline (DataStream API, bounded files).**
- **Sources.** Use the `AppBase`-provided source if one exists. Otherwise `env.readTextFile(path)`, since Flink decompresses `.gz` automatically by extension. Then `.map(TaskEvent::fromString)`, `.filter(e -> e.eventType == 0)`.
- **Watermarks.** The traces are time-sorted, so use `WatermarkStrategy.<TaskEvent>forBoundedOutOfOrderness(Duration.ofSeconds(1)).withTimestampAssigner((e, t) -> e.timestamp / 1000)`. Do the same for job events.
- **Session counts.** `tasks.keyBy(e -> e.jobId).window(EventTimeSessionWindows.withGap(Time.minutes(10))).aggregate(countAgg, (key, win, counts, out) -> out.collect(Tuple2.of(key, counts.iterator().next())))`. A ProcessWindowFunction counting elements also works.
- **Combine with finished jobs.**
  - `sessionCounts.connect(jobs.filter(j -> j.eventType == 4)).keyBy(t -> t.f0, j -> j.jobId).process(new KeyedCoProcessFunction<...>)`.
  - State: `ValueState<Integer> max` and `ValueState<Boolean> finished`.
  - On a session count, update the max.
  - On FINISH, set finished and register an event-time timer at `finishTsMs + 600000 + 1`, so that sessions before the finish have closed.
  - In `onTimer`, if finished and max != null, emit `Tuple2<Long,Integer>(jobId, max)` and clear state.
  - At end of input the final watermark (Long.MAX) fires all pending windows and timers.
- **Sink.** `result.map(t -> "(" + t.f0 + "," + t.f1 + ")")`, or rely on `Tuple2.toString()`, which already prints `(a,b)`. Then `.writeAsText(output, FileSystem.WriteMode.OVERWRITE).setParallelism(1)` so the output is one file, not a directory. Finish with `env.execute("LongestSessionPerJob")`.
- If `writeAsText` is deprecated or unavailable in this version, write a small `RichSinkFunction` with parallelism 1 that appends lines to a `BufferedWriter` and closes it in `close()`.
- Set `env.setParallelism(1)` if in doubt. It is simplest and the data is small.

**5. Datatype classes.**
- Create `TaskEvent` and `JobEvent` as public POJOs: public no-arg constructor, public fields, and a `static fromString(String)`. Match exactly what `AppBase` imports and calls.
- An event-type enum is optional; an int code is fine if `AppBase` doesn't require an enum.

**6. Build and run.**
- `cd /app/workspace && mvn -q -o package -DskipTests 2>&1 | tail -30`. Drop `-o` if offline mode fails.
- `ls target/*.jar`.
- Run with `flink run -c clusterdata.query.LongestSessionPerJob target/<jar> --task_input ... --job_input ... --output /tmp/out.txt` if `which flink` finds it. Otherwise use `java -cp target/<jar> clusterdata.query.LongestSessionPerJob ...`, which works if Flink deps are not `provided` (check the pom scope).
- `head /tmp/out.txt; wc -l /tmp/out.txt`.

**7. Evaluate independently.** Write a short Python check:
- Read both `.gz` files with `gzip.open(..., 'rt')` and the `csv` module.
- Per job, sort SUBMIT timestamps and split stages wherever the consecutive gap is ≥ 600,000,000 µs. Flink's session gap: a new session starts when gap ≥ the gap, so treat exactly-equal as a split.
- Take the max stage size for jobs that have a job FINISH event.
- Compare with the Flink output as sets of `(job, count)`.
- Print only mismatch counts and a few examples.
- Also verify every line matches `^\(\d+,\d+\)$`.

If many mismatches appear, recheck the column indices, the µs→ms conversion, and that SUBMIT is filtered before windowing.
