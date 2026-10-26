import json
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'cvss_provenance.json'
KEYS = {'CVE_ID', 'Severity', 'Score', 'Source', 'CVSS_Version'}


def expected():
    data = json.loads((ROOT / 'trivy_report.json').read_text())
    answer = []
    choices = [('nvd', 'V3Score', 'v3'), ('ghsa', 'V3Score', 'v3'), ('redhat', 'V3Score', 'v3'), ('nvd', 'V2Score', 'v2')]
    for result in data['Results']:
        for v in result.get('Vulnerabilities', []):
            if v['Severity'] not in ('HIGH', 'CRITICAL'):
                continue
            score, source, version = 'N/A', 'N/A', 'N/A'
            for provider, key, cvss_version in choices:
                value = v.get('CVSS', {}).get(provider, {}).get(key)
                if value is not None:
                    score, source, version = round(value, 1), provider, cvss_version
                    break
            answer.append({'CVE_ID': v['VulnerabilityID'], 'Severity': v['Severity'], 'Score': score, 'Source': source, 'CVSS_Version': version})
    return sorted(answer, key=lambda row: row['CVE_ID'])


def actual():
    return json.loads(OUT.read_text(encoding='utf-8'))


def test_file_exists():
    assert OUT.is_file()


def test_schema():
    rows = actual()
    assert isinstance(rows, list)
    assert all(isinstance(row, dict) and set(row) == KEYS for row in rows)


def test_selection_and_order():
    rows = actual()
    assert [(r['CVE_ID'], r['Severity']) for r in rows] == [(r['CVE_ID'], r['Severity']) for r in expected()]


def test_score_and_provenance():
    rows = actual()
    want = expected()
    assert all((r['Score'], r['Source'], r['CVSS_Version']) == (w['Score'], w['Source'], w['CVSS_Version']) for r, w in zip(rows, want))
