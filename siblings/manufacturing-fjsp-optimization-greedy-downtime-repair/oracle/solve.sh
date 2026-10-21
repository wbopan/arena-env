#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_repair.py << 'EOF'
import json, csv
tok = open("instance.txt").read().split()
it = iter(tok)
J = int(next(it)); M = int(next(it))
jobs = []
for _ in range(J):
    ops = []
    for _ in range(int(next(it))):
        k = int(next(it))
        ops.append({int(next(it)): int(next(it)) for _ in range(k)})
    jobs.append(ops)
dt = {}
for r in csv.DictReader(open("downtime.csv")):
    dt.setdefault(int(r["machine"]), []).append((int(r["start"]), int(r["end"])))
base = json.load(open("baseline_solution.json"))["schedule"]
order = sorted(range(len(base)), key=lambda i: (base[i]["op"], base[i]["start"], i))
busy = {m: list(v) for m, v in dt.items()}
new = {}
for i in order:
    r = base[i]
    j, o = r["job"], r["op"]
    al = jobs[j][o]
    m = r["machine"] if r["machine"] in al else sorted(al, key=lambda x: (al[x], x))[0]
    d = al[m]
    t = r["start"] if o == 0 else max(r["start"], new[(j, o - 1)][2])
    while any(t < b and a < t + d for a, b in busy.get(m, [])):
        t += 1
    busy.setdefault(m, []).append((t, t + d))
    new[(j, o)] = (m, t, t + d, d)
with open("repaired.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["job", "op", "machine", "start", "end", "dur"])
    for (j, o) in sorted(new):
        w.writerow([j, o] + list(new[(j, o)]))
EOF
python3 /tmp/solve_repair.py
