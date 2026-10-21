1. Find the Trivy DB (`find / -name trivy.db`) and check that `trivy` exists. Take a quick `head -c` of `/root/package-lock.json`.
2. Run `trivy fs /root/package-lock.json --format json --output /root/trivy_report.json --scanners vuln --skip-db-update --offline-scan --cache-dir <dir containing db/>`.
3. With a Python `csv.DictWriter` script, keep Severity in {HIGH, CRITICAL}. Take CVSS as V3 from nvd, then ghsa, then redhat, else `N/A`. Use FixedVersion or `N/A`, Title, and PrimaryURL.
4. Write `/root/security_audit.csv` with the header `Package,Version,CVE_ID,Severity,CVSS_Score,Fixed_Version,Title,Url`. Then check the header, the severities and the row count against the JSON.
