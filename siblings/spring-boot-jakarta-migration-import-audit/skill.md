## Reference notes

Use Python’s standard library (`pathlib`, `collections.Counter`, `json`). This is a **read-only import audit**: do not rewrite Java sources, run OpenRewrite, or apply the skill documents’ batch `sed` commands.

- Recursively enumerate only `.java` files under `/root/work/src`, including test directories: `root.rglob("*.java")`. Count every such file, even if it has no imports.
- For each line, use `line.strip().startswith("import ")`. A line beginning with `//` or `*` after stripping is not an import. Remove the leading `import `, then an optional leading `static `, and take the name before the first `;`. Count declarations, not distinct names; wildcard and static imports follow the same prefix rules.
- Migrate only names starting with `javax.persistence.`, `javax.validation.`, `javax.servlet.`, `javax.transaction.`, `javax.ws.rs.`, `javax.mail.`, `javax.jms.`, or `javax.xml.bind.`, **except** `javax.transaction.xa.*`. Also migrate exactly `javax.annotation.PostConstruct`, `PreDestroy`, `Resource`, and `Priority` (each qualified with `javax.annotation.`). Unlike the broad mapping in the skill document, other `javax.annotation.*` names stay.
- For a matching prefix, the `by_package` key is that prefix without its final dot, replacing `javax` with `jakarta`; the four exact annotation names count under `jakarta.annotation`. Retain all other imported `javax.*` names, including JDK packages such as `javax.sql.*` and `javax.crypto.*`, in a **distinct, sorted** list.

```python
from pathlib import Path
import json
from collections import Counter

root = Path("/root/work/src")
java_files = sorted(root.rglob("*.java"))
# For each file, read lines, parse qualifying import declarations,
# classify each imported name, and count migrating declarations.
relative_path = file.relative_to(root).as_posix()
```

Keep separate counters for package totals and each file’s migrating-import count. Include a file in `per_file` only when that count is positive; `files_changed` is the number of those files, and `total_migrated_imports` is the sum of their counts. Omit zero-count packages. Write the resulting JSON object to `/root/work/migration_report.json` with exactly the requested keys; then inspect the written JSON and check that the count relationships hold.
