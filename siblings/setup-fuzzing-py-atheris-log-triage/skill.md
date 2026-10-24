## Reference notes

Use Python’s standard-library `pathlib`, `re`, and `json`; these are saved **text logs**, not files to parse with Atheris. The fuzzing skill’s sample shows `#2 INITED`, `#3 NEW`, and `#524288 pulse` status lines, followed by an uncaught-exception marker, an exception line, and a traceback.

- Enumerate `/root/work/logs/*.log`; `Path.stem` gives the library name.
- Recognize status lines only at the start of a line: `r'^#(\d+)\s+(\S+)\b'`. Allow variable spacing and lowercase events such as `pulse`. Extract `cov`, `ft`, and the corpus unit count from that status line, e.g. `r'\bcov:\s*(\d+)\b'`, `r'\bft:\s*(\d+)\b'`, `r'\bcorp:\s*(\d+)/\d+b\b'`. Convert captures with `int()`.
- Update the three `final_*` fields **in file order** on each status line. Independently track `total_execs` with `max()` over captured execution counts, and increment `new_events` only when the event word is exactly `NEW`. Do not treat traceback lines, `INFO:` lines, or crash reports as status lines.
- For the crash marker, comparing `line.strip()` to `=== Uncaught Python exception: ===` accommodates the indentation shown in the skill’s sample. Read the **immediately following line** and obtain the exception type with `next_line.split(': ', 1)[0]`; this preserves dotted names and ignores colons in the message. Use `None` for a non-crashed run; `json.dump()` writes it as `null` and writes Python booleans as JSON booleans.

A compact workflow: inspect filenames and a few representative status/crash lines, write one streaming parser, run it, then inspect the resulting JSON for one entry per log, integer numeric fields, and exactly the requested seven fields per entry.
