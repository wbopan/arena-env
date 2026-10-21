#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import csv, json
from collections import defaultdict, Counter

def norm(s):
    s = s.lower().replace('-', ' ').replace('_', ' ').replace('.', ' ')
    return ' '.join(s.split())

def lev(a, b):
    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        d[i][0] = i
    for j in range(len(b) + 1):
        d[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            d[i][j] = min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + (a[i-1] != b[j-1]))
    return d[len(a)][len(b)]

logs = list(csv.DictReader(open('logs.csv', encoding='utf-8')))
al = defaultdict(list)
for r in csv.DictReader(open('alias_table.csv', encoding='utf-8')):
    al[r['product_id']].append((norm(r['alias']), r['code']))
cb = {}
for r in csv.DictReader(open('codebook.csv', encoding='utf-8')):
    cb[(r['product_id'], r['code'])] = (r['standard_label'], [x for x in r['station_scope'].split('|') if x])
cnt = defaultdict(Counter)
unk = 0
for r in logs:
    pid = r['product_id']
    t = norm(r['reason_text'])
    best = min(((lev(t, a), c) for a, c in al[pid]), default=None)
    code = 'UNKNOWN'
    if best is not None and best[0] <= 2:
        code = best[1]
        scope = cb[(pid, code)][1]
        if scope and r['station'] not in scope:
            code = 'UNKNOWN'
    if code == 'UNKNOWN':
        unk += 1
    cnt[pid][code] += 1
prods = {}
for pid, c in cnt.items():
    n = sum(c.values())
    lst = []
    for code, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])):
        label = '' if code == 'UNKNOWN' else cb[(pid, code)][0]
        lst.append({'code': code, 'label': label, 'count': v, 'share': round(v / n, 4)})
    prods[pid] = lst
json.dump({'total_records': len(logs), 'unknown_records': unk, 'products': prods}, open('pareto.json', 'w'), indent=2)
EOF
python3 /tmp/solve.py
