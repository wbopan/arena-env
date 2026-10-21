#!/bin/bash
set -e
cat > /tmp/solve.py <<'EOF'
import glob, json, os
W = "/root/work"
docs, meets = [], []
for p in glob.glob(os.path.join(W, "DATA", "products", "*.json")):
    d = json.load(open(p, encoding="utf-8"))
    docs += d["documents"]
    meets += d["meetings"]
c = [d for d in docs if d["type"] == "Market Research Report" and "CoachForce" in d["title"]]
s = max(c, key=lambda d: d["date"])
au = set(s["authors"])
rv = set(s["reviewers"])
for m in meets:
    if m["doc_id"] == s["id"]:
        rv |= {t["speaker"] for t in m["transcript"] if t["kind"] == "feedback"}
rv -= au
json.dump({"report_doc_id": s["id"], "author_ids": sorted(au), "reviewer_ids": sorted(rv)}, open(os.path.join(W, "answer.json"), "w"), indent=2)
EOF
python3 /tmp/solve.py
