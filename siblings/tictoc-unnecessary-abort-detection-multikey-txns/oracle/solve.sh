#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import bisect, json
w = {}
for line in open('writes.tsv'):
    p = line.split()
    if p:
        w.setdefault(int(p[1]), []).append(int(p[2]))
for k in w:
    w[k].sort()
ok = {}
for line in open('aborts.tsv'):
    p = line.split()
    if not p:
        continue
    t, k, lw, c = int(p[0]), int(p[1]), int(p[2]), int(p[4])
    l = w.get(k, [])
    i = bisect.bisect_right(l, lw)
    u = i < len(l) and c < l[i]
    ok[t] = ok.get(t, True) and u
res = sorted(t for t, v in ok.items() if v)
json.dump(res, open('unnecessary_aborts.json', 'w'), indent=2)
EOF
python3 /tmp/solve.py
