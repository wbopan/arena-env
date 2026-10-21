#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import bisect, json, csv
w, ab = {}, []
for line in open('trace.jsonl'):
    if not line.strip():
        continue
    e = json.loads(line)
    if e['ev'] == 'write':
        w.setdefault(e['key'], []).append(e['wts'])
    else:
        ab.append(e)
for k in w:
    w[k].sort()
res = {}
for e in ab:
    l = w.get(e['key'], [])
    i = bisect.bisect_right(l, e['local_wts'])
    u = i < len(l) and e['commit_ts'] < l[i]
    t, n = res.get(e['key'], (0, 0))
    res[e['key']] = (t + 1, n + int(u))
with open('abort_report.csv', 'w', newline='') as f:
    wr = csv.writer(f)
    wr.writerow(['key', 'total_aborts', 'unnecessary_aborts', 'rate'])
    for k in sorted(res):
        t, n = res[k]
        wr.writerow([k, t, n, f'{n / t:.4f}'])
EOF
python3 /tmp/solve.py
