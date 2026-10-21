#!/bin/bash
set -e
cat > /tmp/solve.py <<'EOF'
import csv, json, re
W = "/root/work"
msgs = json.load(open(W + "/DATA/slack.json", encoding="utf-8"))
emp = {(r["team"], r["name"]): r["employee_id"] for r in csv.DictReader(open(W + "/DATA/employees.csv", encoding="utf-8"))}
reps = {}
for m in msgs:
    if m["parent_id"]:
        reps.setdefault(m["parent_id"], []).append(m)
out = []
for m in msgs:
    if m["parent_id"] or not m["channel"].startswith("planning-"):
        continue
    mt = re.search(r"/archives/docs/(doc_[0-9a-f]+)", m["text"])
    if not mt:
        continue
    p = m["channel"][9:]
    s = emp[(p, m["user_name"])]
    rs = reps.get(m["id"], [])
    rv = {emp[(p, r["user_name"])] for r in rs if len(r["text"].split()) >= 6} - {s}
    out.append([p, mt.group(1), s, len(rs), ";".join(sorted(rv))])
out.sort(key=lambda r: r[1])
with open(W + "/doc_reviews.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["product", "doc_id", "sharer_id", "n_replies", "reviewer_ids"])
    w.writerows(out)
EOF
python3 /tmp/solve.py
