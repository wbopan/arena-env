# Trivy report to HIGH/CRITICAL CSV

You are a software security engineer. An offline Trivy scan has already been run and its JSON report is at `/root/work/trivy_report.json`. It follows the standard Trivy layout: a top-level `Results` list, where each result has a `Target` and may have a `Vulnerabilities` list. Some results have no vulnerabilities.

Write `/root/work/high_critical.csv` with exactly this header:

`Target,Package,Version,CVE_ID,Severity,CVSS_Score,Fixed_Version,Title,Url`

Write one row per vulnerability entry whose `Severity` is exactly `HIGH` or `CRITICAL`. Fill the columns as follows:

- Target: the result's `Target`.
- Package, Version, CVE_ID, Severity, Title, Url: taken from `PkgName`, `InstalledVersion`, `VulnerabilityID`, `Severity`, `Title` and `PrimaryURL`.
- CVSS_Score: the CVSS v3 score (`V3Score`) from the `CVSS` object. Use the source priority NVD (`nvd`), then GHSA (`ghsa`), then RedHat (`redhat`). Take the first source that has a non-null `V3Score`. Never use `V2Score`. Format the score with exactly one decimal (e.g. `7.0`). If no source has a v3 score, write `N/A`.
- Fixed_Version: copy `FixedVersion` verbatim. If it is missing or empty, write `N/A`.

Row order:

1. Sort by CVSS_Score descending.
2. Put rows with `N/A` scores after all scored rows.
3. Break ties by CVE_ID ascending (string order).

Use standard CSV quoting, because some fields contain commas.
