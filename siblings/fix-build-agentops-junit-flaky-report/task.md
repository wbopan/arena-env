A CI pipeline ran the same pytest suite six times. Each run produced a JUnit XML report, stored as `/root/work/runs/run_01.xml` through `/root/work/runs/run_06.xml`.

Identify tests that are flaky or broken across all runs.

**Test identity.** Each `<testcase>` element is one test result. A test's id is `<classname>::<name>`, built from the testcase's attributes.

**Classifying one testcase:**
- **failed** if it has a `<failure>` or `<error>` child element;
- otherwise **skipped** if it has a `<skipped>` child;
- otherwise **passed**.

Other children, such as `<system-out>`, do not affect the outcome. A test may be absent from some runs.

**Per-test counts:**
- `runs` is the number of non-skipped results (passed plus failed) across all reports.
- `failures` is the number of failed results.

**Statuses:**
- `broken`: `runs > 0` and `failures == runs`;
- `flaky`: `0 < failures < runs`.
- Do not report any other test (for example, tests that always passed or were always skipped).

Write `/root/work/flaky_report.csv`, comma-separated, with this header row:

`test_id,status,runs,failures,fail_rate`

Write one row per reported test, where `fail_rate = failures / runs`, rounded to 3 decimal places.

Sort the rows as follows:
1. All `broken` rows first, then `flaky` rows.
2. Within each status, by `fail_rate` descending (use the unrounded value).
3. Then by `test_id` ascending.
