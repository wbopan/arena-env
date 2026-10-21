#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import json, re

docs = [json.loads(l) for l in open("corpus.jsonl") if l.strip()]
K = json.load(open("config.json"))["num_workers"]
cost, terms = {}, {}
for d in docs:
    t = re.findall(r"[a-z0-9]+", d["text"].lower())
    cost[d["doc_id"]] = len(t)
    terms[d["doc_id"]] = set(t)
order = sorted(cost, key=lambda i: (-cost[i], i))
loads = [0] * K
assign = [[] for _ in range(K)]
for i in order:
    w = min(range(K), key=lambda j: (loads[j], j))
    assign[w].append(i)
    loads[w] += cost[i]
workers = []
for k in range(K):
    s = set()
    for i in assign[k]:
        s |= terms[i]
    workers.append({"worker": k, "doc_ids": assign[k], "load": loads[k], "num_terms": len(s)})
mk = max(loads)
out = {"workers": workers, "makespan": mk, "imbalance": round(mk / (sum(loads) / K), 4)}
json.dump(out, open("schedule.json", "w"), indent=1)
EOF
python3 /tmp/solve.py
