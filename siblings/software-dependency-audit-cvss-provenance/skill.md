## Reference notes

Use Python’s standard-library `json`; the scan report already exists, so no Trivy command or external lookup is needed.

Trivy JSON nests records under `Results[*].Vulnerabilities[*]`. A result may have no `Vulnerabilities`; `CVSS` or an individual source may be absent or JSON-null. Filter on the **input `Severity` label**, not on score ranges. Keep one output element per selected vulnerability record; do not deduplicate by ID.

The score cascade is **NVD v3 → GHSA v3 → Red Hat v3 → NVD v2**. Check `is not None`, not truthiness: `0` is a valid score. Retain the source and version of the chosen score.

```python
choices = (
    ("nvd", "V3Score", "v3"),
    ("ghsa", "V3Score", "v3"),
    ("redhat", "V3Score", "v3"),
    ("nvd", "V2Score", "v2"),
)

cvss = vuln.get("CVSS") or {}
for source, key, version in choices:
    score = (cvss.get(source) or {}).get(key)
    if score is not None:
        # use round(score, 1); retain source and version
        break
else:
    # score, source, version are all "N/A"
    pass
```

Read with `json.load()` from a UTF-8 file. Construct dictionaries containing **only** `CVE_ID`, `Severity`, `Score`, `Source`, and `CVSS_Version`; map `VulnerabilityID` to `CVE_ID`. Keep available scores numeric (`round(score, 1)`, not a formatted string). Sort the list with `key=lambda row: row["CVE_ID"]`, then write the array using `json.dump()` to the specified UTF-8 output file. An empty selection should still produce `[]`.
