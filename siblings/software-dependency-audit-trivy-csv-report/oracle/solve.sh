#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import csv, json

data = json.load(open("trivy_report.json"))
rows = []
for res in data.get("Results", []):
    for v in res.get("Vulnerabilities") or []:
        if v.get("Severity") not in ("HIGH", "CRITICAL"):
            continue
        sc = None
        for s in ("nvd", "ghsa", "redhat"):
            d = (v.get("CVSS") or {}).get(s) or {}
            if d.get("V3Score") is not None:
                sc = float(d["V3Score"])
                break
        rows.append({"Target": res["Target"], "Package": v["PkgName"], "Version": v["InstalledVersion"],
                     "CVE_ID": v["VulnerabilityID"], "Severity": v["Severity"],
                     "CVSS_Score": "N/A" if sc is None else "%.1f" % sc,
                     "Fixed_Version": v.get("FixedVersion") or "N/A",
                     "Title": v.get("Title", ""), "Url": v.get("PrimaryURL", ""), "_s": sc})
rows.sort(key=lambda r: (r["_s"] is None, -(r["_s"] or 0), r["CVE_ID"]))
head = ["Target", "Package", "Version", "CVE_ID", "Severity", "CVSS_Score", "Fixed_Version", "Title", "Url"]
with open("high_critical.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=head, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
EOF
python3 /tmp/solve.py
