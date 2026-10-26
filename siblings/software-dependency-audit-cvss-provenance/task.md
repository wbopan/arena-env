# CVSS score provenance

An offline vulnerability scan is available at `/root/work/trivy_report.json`. Its top-level `Results` array contains Trivy-style vulnerability records. Produce one record for every vulnerability whose `Severity` is exactly `HIGH` or `CRITICAL`; ignore all other severities. Use `VulnerabilityID` as the record identifier.

For each selected vulnerability, choose a score using this priority: `CVSS.nvd.V3Score`, then `CVSS.ghsa.V3Score`, then `CVSS.redhat.V3Score`, then `CVSS.nvd.V2Score`. A missing or JSON-null score does not qualify, but zero does. If none qualifies, report `N/A`. Do not derive severity from the numeric score: the input severity label controls inclusion.

Write exactly one output file, `/root/work/cvss_provenance.json`. It must be a JSON array sorted by `CVE_ID` ascending. Each element must have exactly these fields: `CVE_ID`, `Severity`, `Score`, `Source`, and `CVSS_Version`. `Score` is a JSON number rounded to one decimal place when available, otherwise the string `N/A`. `Source` is `nvd`, `ghsa`, `redhat`, or `N/A`; `CVSS_Version` is `v3`, `v2`, or `N/A`. No external vulnerability lookup is needed.
