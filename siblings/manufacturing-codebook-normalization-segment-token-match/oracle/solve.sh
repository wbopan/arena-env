#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import csv, re

def toks(s):
    return set(re.findall('[a-z0-9]+', s.lower()))

cb = list(csv.DictReader(open('codebook.csv', encoding='utf-8')))
logs = list(csv.DictReader(open('logs.csv', encoding='utf-8')))
rows = []
for r in logs:
    pieces = [p.strip() for p in re.split('[/;+,]', r['raw_reason_text'])]
    pieces = [p for p in pieces if p]
    for i, p in enumerate(pieces, 1):
        T = toks(p)
        best = None
        for c in cb:
            if c['product_id'] != r['product_id']:
                continue
            scope = [x for x in c['station_scope'].split('|') if x]
            if scope and r['station'] not in scope:
                continue
            K = toks(c['standard_label'])
            for k in c['keywords'].split('|'):
                K |= toks(k)
            s = len(T & K) / len(T) if T else 0.0
            if best is None or s > best[0] or (s == best[0] and c['code'] < best[1]['code']):
                best = (s, c)
        s = best[0] if best else 0.0
        if best is None or s < 0.5:
            code, label = 'UNKNOWN', ''
        else:
            code, label = best[1]['code'], best[1]['standard_label']
        rows.append([r['record_id'] + '-S' + str(i), r['record_id'], p, code, label, '%.4f' % s])
with open('segments.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['segment_id', 'record_id', 'span_text', 'pred_code', 'pred_label', 'score'])
    w.writerows(rows)
EOF
python3 /tmp/solve.py
