#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import csv, json, re

def clean(v):
    v = v.strip()
    if v.endswith(','):
        v = v[:-1].strip()
    if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
        v = v[1:-1]
    return v.replace('{', '').replace('}', '').strip()

entries = []
cur = None
for line in open('refs.bib', encoding='utf-8'):
    m = re.match(r'^\s*@(\w+)\s*\{\s*([^,\s]+)\s*,', line)
    if m:
        cur = (m.group(2), {})
        entries.append(cur)
        continue
    if cur is None:
        continue
    if re.match(r'^\s*\}\s*$', line):
        cur = None
        continue
    m = re.match(r'^\s*([A-Za-z_]+)\s*=\s*(.*)$', line)
    if m:
        cur[1][m.group(1).lower()] = clean(m.group(2))

def ndoi(d):
    d = d.strip().lower()
    for p in ('https://doi.org/', 'http://doi.org/', 'https://dx.doi.org/', 'http://dx.doi.org/', 'doi:'):
        if d.startswith(p):
            d = d[len(p):]
            break
    return d.strip()

def nt(t):
    t = t.replace('\\', '').replace('{', '').replace('}', '').lower()
    return re.sub(r'[^a-z0-9]+', ' ', t).strip()

reg = {ndoi(r['doi']): r for r in csv.DictReader(open('registry.csv', newline=''))}
reasons = {}
for key, f in entries:
    d = ndoi(f.get('doi', ''))
    if not d:
        reasons[key] = 'missing_doi'
    elif d not in reg:
        reasons[key] = 'unknown_doi'
    elif nt(f.get('title', '')) != nt(reg[d]['title']):
        reasons[key] = 'title_mismatch'
    elif f.get('year', '').strip() != reg[d]['year'].strip():
        reasons[key] = 'year_mismatch'
json.dump({'fake_keys': sorted(reasons), 'reasons': reasons}, open('audit.json', 'w'), indent=2)
EOF
python3 /tmp/solve.py
