#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_installed_map.py <<'PY'
import json
from pathlib import Path

root = Path('/root/work')
lock = json.loads((root / 'package-lock.json').read_text())
scan = json.loads((root / 'trivy_report.json').read_text())
by_install = {}
for result in scan['Results']:
    for vuln in result.get('Vulnerabilities', []):
        if vuln['Severity'] in ('HIGH', 'CRITICAL'):
            by_install.setdefault((vuln['PkgName'], vuln['InstalledVersion']), []).append(vuln)
rows = {}
for path, entry in lock['packages'].items():
    if path == '':
        continue
    name = path.rsplit('node_modules/', 1)[1]
    for vuln in by_install.get((name, entry['version']), []):
        cve = vuln['VulnerabilityID']
        rows[(path, cve)] = {'Path': path, 'Package': name, 'Version': entry['version'], 'CVE_ID': cve, 'Fixed_Version': vuln.get('FixedVersion') or 'N/A'}
answer = [rows[key] for key in sorted(rows)]
(root / 'installed_findings.json').write_text(json.dumps(answer, indent=2) + '\n')
PY
python /tmp/solve_installed_map.py
