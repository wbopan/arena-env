#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_lru.py <<'EOF'
import csv
import json
from collections import OrderedDict

cfg = json.load(open("config.json"))
bs = cfg["block_size"]
cap = cfg["cache_capacity_blocks"]
reqs = [json.loads(l) for l in open("trace.jsonl") if l.strip()]
order = sorted(range(len(reqs)), key=lambda i: (reqs[i]["timestamp"], i))
lru = OrderedDict()
with open("hits.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["request_id", "timestamp", "prompt_tokens", "hit_blocks", "hit_tokens"])
    for i in order:
        r = reqs[i]
        k = 0
        for h in r["hash_ids"]:
            if h in lru:
                k += 1
            else:
                break
        for h in r["hash_ids"]:
            if h in lru:
                lru.move_to_end(h)
            else:
                lru[h] = True
                if len(lru) > cap:
                    lru.popitem(last=False)
        w.writerow([r["request_id"], r["timestamp"], r["input_length"], k,
                    min(k * bs, r["input_length"])])
EOF
python3 /tmp/solve_lru.py
