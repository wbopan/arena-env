## Reference notes

Use Python’s standard-library `json` module. The Trivy-style report is already provided; **do not run Trivy** or use CVSS scores to reinterpret severity.

```python
import json

with open("/root/work/package-lock.json", encoding="utf-8") as f:
    lock = json.load(f)
with open("/root/work/trivy_report.json", encoding="utf-8") as f:
    report = json.load(f)
```

- Iterate `lock["packages"].items()`, skipping path `""`. For an installation path, derive the package name with `path.rsplit("node_modules/", 1)[1]`; this retains scoped names such as `@scope/name`. Read the installed version from that entry’s `version`.
- Iterate **every** `result` in `report.get("Results", [])`, then `result.get("Vulnerabilities", [])`. Relevant finding fields are `PkgName`, `InstalledVersion`, `VulnerabilityID`, `Severity`, and `FixedVersion`.
- Keep only `Severity in {"HIGH", "CRITICAL"}`. Match **both** `PkgName` and `InstalledVersion` exactly against an installed instance. One finding can match several paths; unmatched findings contribute no rows.
- Deduplicate on `(Path, VulnerabilityID)`. Set `Fixed_Version` to `finding.get("FixedVersion") or "N/A"` so missing, null, and empty values use the fallback.
- Each output dictionary must contain **only** `Path`, `Package`, `Version`, `CVE_ID`, and `Fixed_Version`. Sort rows with `key=lambda row: (row["Path"], row["CVE_ID"])`, then write the array using `json.dump(rows, f, indent=2)` to `/root/work/installed_findings.json`.

A compact workflow: inspect the two top-level JSON shapes, build an index from `(package name, version)` to installation paths, traverse the report and collect unique matching path/ID pairs, then sort and write the JSON array.
