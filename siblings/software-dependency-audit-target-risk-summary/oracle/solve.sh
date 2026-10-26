#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_target_risk.py <<'PY'
import csv
import json
from collections import defaultdict
from pathlib import Path

root = Path('/root/work')
data = json.loads((root / 'trivy_report.json').read_text())
by_target = defaultdict(list)
for result in data['Results']:
    by_target[result['Target']] += result.get('Vulnerabilities', [])
fields = ['Target', 'High_CVEs', 'Critical_CVEs', 'Affected_Packages', 'Max_CVSS']
with (root / 'target_risk.csv').open('w', newline='', encoding='utf-8') as output:
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for target in sorted(by_target):
        findings = [v for v in by_target[target] if v['Severity'] in ('HIGH', 'CRITICAL')]
        maxima = []
        for v in findings:
            for provider in ('nvd', 'ghsa', 'redhat'):
                score = v.get('CVSS', {}).get(provider, {}).get('V3Score')
                if score is not None:
                    maxima.append(score)
                    break
        writer.writerow({'Target': target, 'High_CVEs': len({v['VulnerabilityID'] for v in findings if v['Severity'] == 'HIGH'}), 'Critical_CVEs': len({v['VulnerabilityID'] for v in findings if v['Severity'] == 'CRITICAL'}), 'Affected_Packages': len({(v['PkgName'], v['InstalledVersion']) for v in findings}), 'Max_CVSS': f'{max(maxima):.1f}' if maxima else 'N/A'})
PY
python /tmp/solve_target_risk.py
