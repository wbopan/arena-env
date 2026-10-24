## Reference notes

Use Python’s standard-library `pathlib`, `re`, `collections.Counter`, and `json`; no CI-analysis CLI or Temporal tooling is needed for a local log.

- Each raw line has a timestamp followed by **one space**. Remove only that prefix: `line.partition(" ")[2].rstrip("\r\n")`. Apply section and entry checks to the resulting text.
- Enter the section after a line containing `short test summary info`. Stop **before** the next timestamp-stripped line whose first character is `=`. Do not count similarly formatted lines outside these boundaries.
- Within the section, accept only lines beginning `FAILED ` or `ERROR `. Split an entry at its first ` - ` into `<KIND> <nodeid>` and `<exception>`; nodeids can contain `::`. The exception type is `exception.split(":", 1)[0]`; the file is `nodeid.split("::", 1)[0]`.
- Only for exception type **exactly** `ModuleNotFoundError`, look for `No module named '<name>'` in its exception text. Add `name.split(".", 1)[0]` to a set; output `sorted(modules)`.
- Count kinds, exception types, and files separately. For a nonempty file counter, the tie rule can be expressed as `min(file_counts, key=lambda p: (-file_counts[p], p))`.

Compact parsing primitives:

```python
from collections import Counter
from pathlib import Path
import json
import re

text = Path("/root/work/ci_log.txt").read_text()
module_pattern = re.compile(r"No module named '([^']+)'")

for raw in text.splitlines():
    line = raw.partition(" ")[2]  # discard timestamp and its separating space
    # Track whether line is inside the short-summary boundaries.
    # Parse qualifying entries and update Counters / module set here.
```

Write the resulting object with `Path("/root/work/ci_summary.json").write_text(json.dumps(result, indent=2) + "\n")`. After running the script, read the JSON back and check that it has exactly the five requested keys and that counts come only from the bounded section.
