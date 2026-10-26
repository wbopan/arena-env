## Reference notes

Use Python’s standard-library `json` and `csv`; the report already exists, so no Trivy scan is needed.

- Read with `json.load(open(path, encoding="utf-8"))`. Iterate `data.get("Results", [])`; each result has a `Target` and may have `Vulnerabilities`. Create the target’s summary state **before** iterating vulnerabilities so targets with no selected findings remain in the output. Merge results that share a target.
- Select records by `vuln.get("Severity") in ("HIGH", "CRITICAL")` only. Do not infer severity from a CVSS score.
- Maintain separate `set`s of `VulnerabilityID` for HIGH and CRITICAL, and a third set of `(PkgName, InstalledVersion)` tuples across both selected severities. Use each set’s length for its count.
- For each selected **record**, take the first non-null `V3Score` in source order; never fall back to `V2Score`:

```python
def v3_score(vuln):
    cvss = vuln.get("CVSS") or {}
    for source in ("nvd", "ghsa", "redhat"):
        entry = cvss.get(source) or {}
        score = entry.get("V3Score")
        if score is not None:  # 0.0 is a valid value
            return score
    return None
```

Compare available record scores to obtain the target maximum; an unscored record does not contribute. Format an available maximum with `f"{score:.1f}"`, otherwise use `"N/A"`.

Write the exact requested header and one row per target, ordered by `sorted(targets)`. For UTF-8 CSV, use `open(output_path, "w", encoding="utf-8", newline="")`, then `csv.writer(...).writerow(header)` and `writerow(...)` for each row. `newline=""` avoids extra CSV line breaks. Keep the file to the header and summary rows—no metadata or blank separator rows.

Short workflow: inspect the JSON structure cheaply, write one Python script using per-target sets and score state, run it, then read back the CSV header and rows to check ordering and formatting.
