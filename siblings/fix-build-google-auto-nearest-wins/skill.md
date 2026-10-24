## Reference notes

Use Python’s standard library (`xml.etree.ElementTree`, `json`, `collections.deque`); no Maven command is needed. The task specifies the mediation procedure, so do not substitute Maven’s full dependency-management or scope rules.

```python
import json
import xml.etree.ElementTree as ET
from collections import deque
from pathlib import Path

base = Path("/root/work")
ns = {"m": "http://maven.apache.org/POM/4.0.0"}
root = ET.parse(base / "pom.xml").getroot()
direct = root.findall("./m:dependencies/m:dependency", ns)
repo = json.loads((base / "repository.json").read_text(encoding="utf-8"))
```

- Use `./m:dependencies/m:dependency`, not `.//m:dependency`: only the root project’s direct dependencies seed the queue. Read each child’s namespaced `groupId`, `artifactId`, and `version` in XML order. Include direct dependencies even when their `<optional>` is `true`.
- Repository keys and each dependency’s `coord` are `groupId:artifactId:version`; its `optional` field is a JSON boolean. Skip **optional repository dependencies** when appending children, not when seeding direct dependencies.
- Queue entries need a coordinate and integer depth. Seed a `deque` at depth 1; use `popleft()` and append children in repository-list order at depth + 1. Key the resolved map by `groupId:artifactId`, **not** by full coordinate. On a repeated key, discard the entry without expanding it. FIFO order makes the first processed version the nearest, with declaration order breaking equal-depth ties.
- Sort output by the `groupId:artifactId` key using ordinary Python string sorting. Write each saved coordinate and depth as `f"{coord} {depth}"`, one line per artifact, no header or blank lines. Exclude the root project. Inspect the output file briefly after running the script.
