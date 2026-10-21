#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import csv, re
REQ = {'article': ['author', 'title', 'journal', 'year'],
       'inproceedings': ['author', 'title', 'booktitle', 'year'],
       'book': ['author', 'title', 'publisher', 'year'],
       'misc': ['author', 'title', 'year']}

def clean(v):
    v = v.strip()
    if v.endswith(','):
        v = v[:-1].strip()
    if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
        v = v[1:-1]
    return v.replace('{', '').replace('}', '').strip()

entries = []
cur = None
for line in open('library.bib', encoding='utf-8'):
    m = re.match(r'^\s*@(\w+)\s*\{\s*([^,\s]+)\s*,', line)
    if m:
        cur = (m.group(2), m.group(1).lower(), {})
        entries.append(cur)
        continue
    if cur is None:
        continue
    if re.match(r'^\s*\}\s*$', line):
        cur = None
        continue
    m = re.match(r'^\s*([A-Za-z_]+)\s*=\s*(.*)$', line)
    if m:
        cur[2][m.group(1).lower()] = clean(m.group(2))

rows = []
for key, et, f in entries:
    miss = []
    for fl in REQ.get(et, []):
        v = f.get(fl, '')
        if v == '' or (fl == 'year' and not re.fullmatch(r'\d{4}', v)):
            miss.append(fl)
    if miss:
        rows.append([key, et, ';'.join(miss)])
rows.sort(key=lambda r: r[0])
with open('missing_fields.csv', 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['key', 'entry_type', 'missing_fields'])
    w.writerows(rows)
EOF
python3 /tmp/solve.py
