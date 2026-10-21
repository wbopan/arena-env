# Triage Atheris fuzzing logs

Several Python libraries were fuzzed with Atheris (libFuzzer engine). The fuzzer output of each run was saved as `/root/work/logs/<lib>.log`. The library name is the file name without the `.log` extension.

A libFuzzer status line starts with `#<N>` (the execution count), followed by an event word such as `INITED`, `NEW`, `REDUCE`, `pulse` or `DONE`. It then carries fields like `cov: <int> ft: <int> corp: <units>/<bytes>b ...`. Lines that do not start with `#<digits>` are not status lines. Examples are `INFO:` lines, tracebacks and crash reports.

A run crashed if its log contains the line `=== Uncaught Python exception: ===`. The line right after it has the form `<ExceptionType>: <message>`. The exception type is everything before the first `": "`, kept exactly as printed, including any dotted module path.

For every log, compute these values:

- `final_cov`: the `cov` value on the last status line.
- `final_ft`: the `ft` value on the last status line.
- `final_corpus_units`: the corpus unit count (the number before `/`) on the last status line.
- `total_execs`: the largest `#<N>` over all status lines.
- `new_events`: the number of status lines whose event word is `NEW`.
- `crashed`: a boolean.
- `exception_type`: a string, or `null` if the run did not crash.

Write `/root/work/fuzz_summary.json`. It must be one JSON object that maps each library name to an object with exactly the seven keys above. All numeric values are integers.
