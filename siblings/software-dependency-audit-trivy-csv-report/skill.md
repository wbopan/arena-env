## Reference notes

Use Python standard-library `json` and `csv`; the scan is already complete, so do not run Trivy. Read `/root/work/trivy_report.json` with `json.load`. Iterate `data.get("Results", [])`; each result supplies `Target`, and `result.get("Vulnerabilities") or []` handles absent or null vulnerability lists. Keep entries only when `vuln.get("Severity") in ("HIGH", "CRITICAL")`—do not infer inclusion from the numeric score.

Field mapping, in required header order:

| CSV column | JSON field |
|---|---|
| Target | result `Target` |
| Package, Version, CVE_ID | vulnerability `PkgName`, `InstalledVersion`, `VulnerabilityID` |
| Severity, Title, Url | vulnerability `Severity`, `Title`, `PrimaryURL` |
| Fixed_Version | vulnerability `FixedVersion`; use `N/A` if missing or empty |

Extract **only** `V3Score`, checking sources in order. A score of `0` is present, not missing:

```python
def v3_score(vuln):
    cvss = vuln.get("CVSS") or {}
    for source in ("nvd", "ghsa", "redhat"):
        entry = cvss.get(source) or {}
        score = entry.get("V3Score")
        if score is not None:
            return score
    return None
```

Keep the score numeric until after sorting. A suitable key for a record holding its numeric score and CVE ID is:

```python
(score is None, -(score if score is not None else 0), cve_id)
```

This orders scored rows descending, then `N/A` rows, with CVE_ID ascending on ties. For CSV output, format a present score as `f"{score:.1f}"`; otherwise write `"N/A"`. Never fall back to `V2Score`.

Use `csv.DictWriter` with the **exact header from the task**, `writeheader()`, and `writerows(...)`. Open the output with `encoding="utf-8", newline=""` so fields containing commas or line breaks receive standard CSV quoting. Write the header even if there are no matching rows.

Efficient workflow: inspect only the JSON’s top-level shape and a small sample if needed; write one short conversion script; run it; briefly inspect the CSV header and a few rows without dumping the whole report.
