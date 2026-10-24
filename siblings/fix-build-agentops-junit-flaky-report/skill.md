## Reference notes

Use Python’s standard-library `xml.etree.ElementTree` and `csv`; the CI-log and pytest-testing tools in the supplied documents are not needed for existing JUnit reports.

```python
from pathlib import Path
import xml.etree.ElementTree as ET
import csv

for path in sorted(Path("/root/work/runs").glob("run_*.xml")):
    root = ET.parse(path).getroot()
    for case in root.iter("testcase"):
        test_id = f"{case.attrib['classname']}::{case.attrib['name']}"
        child_tags = {child.tag for child in case}  # direct children only
        # classify this result, then update counts for test_id
```

- A `<failure>` **or** `<error>` wins over `<skipped>`; otherwise a skipped child means skipped; otherwise passed. Ignore children such as `<system-out>`. Count each `<testcase>` element as one result; do not infer results for tests absent from a report.
- For each id, `runs = passed + failed` and `failures = failed`. Skipped results contribute to neither. With `runs > 0`, report `broken` when `failures == runs`, or `flaky` when `0 < failures < runs`.
- Sort using the **unrounded** rate: key `(0 if status == "broken" else 1, -failures / runs, test_id)`. Format the rate for CSV separately with `f"{failures / runs:.3f}"`.
- Write with `csv.writer`, `open("/root/work/flaky_report.csv", "w", newline="", encoding="utf-8")`, and the exact header `["test_id", "status", "runs", "failures", "fail_rate"]`. CSV writing handles commas or quoting in test ids.
- After running the script, inspect the header and a few rows of the output, including their ordering.
