import json
import random

random.seed(4107)
patterns = [
    {'nvd': {'V3Score': None, 'V2Score': 6.4}, 'ghsa': {'V3Score': 8.1}},
    {'nvd': {'V3Score': 9.8}, 'ghsa': {'V3Score': 7.2}},
    {'redhat': {'V3Score': 7.6}},
    {'nvd': {'V2Score': 7.5}},
    {'nvd': {'V3Score': None}, 'ghsa': {'V3Score': None}},
    {'nvd': {'V3Score': 0.0}, 'redhat': {'V3Score': 9.0}},
]
results = []
for target in ['package-lock.json', 'vendor/package-lock.json']:
    vulns = []
    for i in range(7):
        number = 5000 + len(results) * 7 + i
        vulns.append({
            'VulnerabilityID': f'CVE-2025-{number}',
            'PkgName': random.choice(['atlas', 'bridge', 'cipher', 'delta']),
            'Severity': random.choice(['HIGH', 'CRITICAL', 'MEDIUM', 'LOW']),
            'CVSS': random.choice(patterns),
        })
    random.shuffle(vulns)
    results.append({'Target': target, 'Vulnerabilities': vulns})
with open('trivy_report.json', 'w', encoding='utf-8') as f:
    json.dump({'Results': results}, f, indent=2)
