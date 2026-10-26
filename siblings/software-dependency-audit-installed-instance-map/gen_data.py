import json
import random

random.seed(9305)
packages = {'': {'name': 'sample-app', 'version': '1.0.0'}}
entries = [
    ('node_modules/alpha', '1.0.0'),
    ('node_modules/beta', '2.1.0'),
    ('node_modules/@field/codec', '3.0.0'),
    ('node_modules/tool/node_modules/alpha', '1.0.0'),
    ('node_modules/web/node_modules/beta', '1.9.0'),
    ('node_modules/delta', '4.0.0'),
    ('node_modules/epsilon', '2.0.0'),
]
random.shuffle(entries)
for path, version in entries:
    packages[path] = {'version': version}
with open('package-lock.json', 'w', encoding='utf-8') as f:
    json.dump({'name': 'sample-app', 'lockfileVersion': 3, 'packages': packages}, f, indent=2)
findings = []
for i, (name, version) in enumerate([('alpha', '1.0.0'), ('beta', '2.1.0'), ('@field/codec', '3.0.0'), ('beta', '1.9.0'), ('delta', '4.0.0'), ('epsilon', '2.0.0'), ('alpha', '9.0.0'), ('missing', '1.0.0')]):
    findings.append({'PkgName': name, 'InstalledVersion': version, 'VulnerabilityID': f'CVE-2025-{7300+i}', 'Severity': random.choice(['HIGH', 'CRITICAL', 'MEDIUM']), 'FixedVersion': random.choice(['', '5.0.0', '2.2.1'])})
findings.append(dict(findings[0]))
random.shuffle(findings)
with open('trivy_report.json', 'w', encoding='utf-8') as f:
    json.dump({'Results': [{'Target': 'package-lock.json', 'Vulnerabilities': findings[:5]}, {'Target': 'nested dependencies', 'Vulnerabilities': findings[5:]}]}, f, indent=2)
