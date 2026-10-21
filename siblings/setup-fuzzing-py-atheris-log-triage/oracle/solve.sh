#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import json, os, re
rx = re.compile(r'^#(\d+)\s+(\S+)\s+cov: (\d+) ft: (\d+) corp: (\d+)/')
out = {}
for fn in sorted(os.listdir('logs')):
    if not fn.endswith('.log'):
        continue
    lines = open(os.path.join('logs', fn)).read().splitlines()
    st = []
    for l in lines:
        m = rx.match(l)
        if m:
            st.append((int(m[1]), m[2], int(m[3]), int(m[4]), int(m[5])))
    exc = None
    for i, l in enumerate(lines):
        if l.strip() == '=== Uncaught Python exception: ===':
            exc = lines[i + 1].split(': ', 1)[0]
            break
    last = st[-1]
    out[fn[:-4]] = {
        'final_cov': last[2], 'final_ft': last[3], 'final_corpus_units': last[4],
        'total_execs': max(s[0] for s in st),
        'new_events': sum(1 for s in st if s[1] == 'NEW'),
        'crashed': exc is not None, 'exception_type': exc,
    }
json.dump(out, open('fuzz_summary.json', 'w'), indent=2)
EOF
python3 /tmp/solve.py
