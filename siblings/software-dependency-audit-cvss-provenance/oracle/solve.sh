#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_cvss_provenance.py <<'PY'
import json
from pathlib import Path

root = Path('/root/work')
data = json.loads((root / 'trivy_report.json').read_text())
rows = []
for result in data['Results']:
    for item in result.get('Vulnerabilities', []):
        if item['Severity'] not in {'HIGH', 'CRITICAL'}:
            continue
        score, source, version = 'N/A', 'N/A', 'N/A'
        for name, field, release in [('nvd', 'V3Score', 'v3'), ('ghsa', 'V3Score', 'v3'), ('redhat', 'V3Score', 'v3'), ('nvd', 'V2Score', 'v2')]:
            candidate = item.get('CVSS', {}).get(name, {}).get(field)
            if candidate is not None:
                score, source, version = round(candidate, 1), name, release
                break
        rows.append({'CVE_ID': item['VulnerabilityID'], 'Severity': item['Severity'], 'Score': score, 'Source': source, 'CVSS_Version': version})
rows.sort(key=lambda row: row['CVE_ID'])
(root / 'cvss_provenance.json').write_text(json.dumps(rows, indent=2) + '\n')
PY
python /tmp/solve_cvss_provenance.py
