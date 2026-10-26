import json
import random

random.seed(8224)
results = []
targets = ['apps/api/package-lock.json', 'apps/web/package-lock.json', 'tools/package-lock.json']
for t, target in enumerate(targets):
    for batch in range(2):
        items = []
        for j in range(4):
            severity = 'LOW' if t == 2 else random.choice(['HIGH', 'CRITICAL', 'MEDIUM'])
            ident = f'CVE-2024-{6100 + t * 20 + j}'
            cvss = random.choice([
                {'nvd': {'V3Score': 8.2}, 'ghsa': {'V3Score': 9.1}},
                {'ghsa': {'V3Score': 7.4}},
                {'redhat': {'V3Score': 9.3}},
                {'nvd': {'V2Score': 6.8}},
                {},
            ])
            items.append({'VulnerabilityID': ident, 'Severity': severity, 'PkgName': ['argon', 'boron', 'carbon'][j % 3], 'InstalledVersion': f'1.{j % 2}.0', 'CVSS': cvss})
        results.append({'Target': target, 'Vulnerabilities': items})
random.shuffle(results)
with open('trivy_report.json', 'w', encoding='utf-8') as f:
    json.dump({'Results': results}, f, indent=2)
