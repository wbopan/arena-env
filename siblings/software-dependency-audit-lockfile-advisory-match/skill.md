## Reference notes

Use Python’s standard-library `json`; the supplied `advisories.json` is the database. Trivy and its database format do not apply here.

```python
import json

with open("/root/work/package-lock.json", encoding="utf-8") as f:
    lock = json.load(f)
with open("/root/work/advisories.json", encoding="utf-8") as f:
    advisory_data = json.load(f)

def version_key(version):
    return tuple(int(part) for part in version.split("."))
```

- Installed entries are `lock["packages"]` items except key `""`. Extract a name with `path.rsplit("node_modules/", 1)[-1]`; this preserves scoped names such as `@x/y`. Deduplicate `(name, entry["version"])` pairs before matching.
- Compare versions using numeric `(major, minor, patch)` tuples, **not** strings. A range matches when `introduced <= version` and either `fixed is None` or `version < fixed`. An advisory matches if **any** of its ranges matches; overlapping ranges must not produce duplicate findings.
- Select `cvss_v3` when it is **not `None`**, otherwise `cvss_v2`; retain `None` when both are null. Do not use truthiness for the fallback. Apply the requested CVSS v3 bands to the selected score and use `UNKNOWN` for null. The skill document lists 0.0 as “None,” but the requested output specifies no `NONE` summary key.
- Sort findings with a key shaped like `(finding["package"], version_key(finding["version"]), finding["advisory"])`. Initialize all five requested summary keys to zero, then count findings by severity. Count distinct package **names** in findings for `affected_packages`.

Write the final object with `json.dump(...)` to `/root/work/audit.json`. A compact workflow is: inspect the JSON structures briefly, write one Python script to load/deduplicate/match/sort/count/write, run it, then inspect the output JSON and its finding count.
