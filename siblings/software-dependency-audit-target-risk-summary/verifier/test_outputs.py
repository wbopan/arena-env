import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'target_risk.csv'
HEADER = ['Target', 'High_CVEs', 'Critical_CVEs', 'Affected_Packages', 'Max_CVSS']


def expected():
    report = json.loads((ROOT / 'trivy_report.json').read_text())
    groups = defaultdict(list)
    for result in report['Results']:
        groups[result['Target']].extend(result.get('Vulnerabilities', []))
    summary = []
    for target in sorted(groups):
        chosen = [v for v in groups[target] if v['Severity'] in ('HIGH', 'CRITICAL')]
        scores = []
        for v in chosen:
            for source in ('nvd', 'ghsa', 'redhat'):
                value = v.get('CVSS', {}).get(source, {}).get('V3Score')
                if value is not None:
                    scores.append(value)
                    break
        summary.append({'Target': target, 'High_CVEs': str(len({v['VulnerabilityID'] for v in chosen if v['Severity'] == 'HIGH'})), 'Critical_CVEs': str(len({v['VulnerabilityID'] for v in chosen if v['Severity'] == 'CRITICAL'})), 'Affected_Packages': str(len({(v['PkgName'], v['InstalledVersion']) for v in chosen})), 'Max_CVSS': f'{max(scores):.1f}' if scores else 'N/A'})
    return summary


def read():
    with OUT.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def test_file_exists():
    assert OUT.is_file()


def test_header_and_columns():
    header, rows = read()
    assert header == HEADER
    assert all(set(row) == set(HEADER) for row in rows)


def test_targets_and_counts():
    _, rows = read()
    want = expected()
    assert [[r[k] for k in HEADER[:4]] for r in rows] == [[r[k] for k in HEADER[:4]] for r in want]


def test_maximum_v3_scores():
    _, rows = read()
    assert [r['Max_CVSS'] for r in rows] == [r['Max_CVSS'] for r in expected()]
