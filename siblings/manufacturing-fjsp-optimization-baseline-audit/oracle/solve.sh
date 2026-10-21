#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_audit.py << 'EOF'
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
rows = json.load(open("baseline_solution.json"))["schedule"]
def ov(a, b, c, d):
    return a < d and c < b
ill = sum(1 for r in rows if r["machine"] not in jobs[r["job"]][r["op"]])
mis = sum(1 for r in rows if r["machine"] in jobs[r["job"]][r["op"]]
          and r["end"] - r["start"] != jobs[r["job"]][r["op"]][r["machine"]])
bm = {(r["job"], r["op"]): r for r in rows}
prec = sum(1 for (j, o), r in bm.items() if (j, o + 1) in bm and r["end"] > bm[(j, o + 1)]["start"])
mo = sum(1 for i in range(len(rows)) for k in range(i + 1, len(rows))
         if rows[i]["machine"] == rows[k]["machine"]
         and ov(rows[i]["start"], rows[i]["end"], rows[k]["start"], rows[k]["end"]))
dv = sum(1 for r in rows if any(ov(r["start"], r["end"], s, e) for s, e in dt.get(r["machine"], [])))
out = {"makespan": max(r["end"] for r in rows), "illegal_machine": ill,
       "duration_mismatch": mis, "precedence_violations": prec,
       "machine_overlaps": mo, "downtime_violations": dv,
       "feasible": ill + mis + prec + mo + dv == 0}
json.dump(out, open("audit.json", "w"), indent=2)
EOF
python3 /tmp/solve_audit.py
