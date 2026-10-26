## Reference notes

Use **Python’s standard library**; no fuzzing framework or project environment is needed. Inspect filenames cheaply, then read each candidate with `Path.read_bytes()`. Do not decode before measuring length or computing the digest.

```python
from pathlib import Path
import csv, hashlib, json

seed_dir = Path("/root/work/seeds")
for path in seed_dir.iterdir():
    if not path.is_file():
        continue
    raw = path.read_bytes()
    size = len(raw)
    digest = hashlib.sha256(raw).hexdigest()
    filename = path.name
```

- Classify in order: `raw.decode("utf-8")` succeeds → try `json.loads(decoded)`; a successful parse of **any JSON value**, not just an object or array, means `json`. Catch `json.JSONDecodeError` for valid UTF-8 that is not JSON (`text`); catch `UnicodeDecodeError` for `binary`.
- JSON deduplication key: `json.dumps(parsed, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`. Use the original `raw` bytes as the key for `text` and `binary`. Keep keys separate by category.
- For each `(category, key)`, retain the candidate with the smallest `(len(raw), filename)` tuple. Sort retained candidates within each category by that same tuple and take at most two.
- Emit categories explicitly in `json`, `text`, `binary` order. Write the exact header and selected rows as UTF-8 TSV; `csv.writer(..., delimiter="\t", lineterminator="\n")` with `open(..., "w", encoding="utf-8", newline="")` handles line endings. `bytes` and SHA-256 must describe the **original bytes**, not normalized JSON or decoded text.

After running the script, inspect the manifest’s header and rows and confirm that the seed directory was not changed.
