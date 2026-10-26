import json
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'installed_findings.json'
FIELDS = {'Path', 'Package', 'Version', 'CVE_ID', 'Fixed_Version'}


def expected():
    lock = json.loads((ROOT / 'package-lock.json').read_text())
    report = json.loads((ROOT / 'trivy_report.json').read_text())
    findings = [v for result in report['Results'] for v in result.get('Vulnerabilities', []) if v['Severity'] in ('HIGH', 'CRITICAL')]
    rows = {}
    for path, details in lock['packages'].items():
        if not path:
            continue
        package = path.rsplit('node_modules/', 1)[-1]
        version = details['version']
        for finding in findings:
            if (finding['PkgName'], finding['InstalledVersion']) != (package, version):
                continue
            identifier = finding['VulnerabilityID']
            rows[(path, identifier)] = {'Path': path, 'Package': package, 'Version': version, 'CVE_ID': identifier, 'Fixed_Version': finding.get('FixedVersion') or 'N/A'}
    return [rows[key] for key in sorted(rows)]


def actual():
    return json.loads(OUT.read_text(encoding='utf-8'))


def test_file_exists():
    assert OUT.is_file()


def test_json_schema():
    rows = actual()
    assert isinstance(rows, list)
    assert all(isinstance(row, dict) and set(row) == FIELDS for row in rows)


def test_matching_instances_and_order():
    rows = actual()
    want = expected()
    assert [(r['Path'], r['Package'], r['Version'], r['CVE_ID']) for r in rows] == [(r['Path'], r['Package'], r['Version'], r['CVE_ID']) for r in want]


def test_fixed_versions():
    assert [r['Fixed_Version'] for r in actual()] == [r['Fixed_Version'] for r in expected()]
