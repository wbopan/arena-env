#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_sweep.py <<'EOF'
import json
from collections import OrderedDict

cfg = json.load(open("config.json"))
bs = cfg["block_size"]
trace = [json.loads(l) for l in open("trace.jsonl") if l.strip()]
total = sum(r["input_length"] for r in trace)


def run(policy, cap):
    order = OrderedDict()
    freq = {}
    admit = {}
    clock = 0
    hits = 0
    evictions = 0
    for r in trace:
        k = 0
        for h in r["hash_ids"]:
            if h not in order:
                break
            k += 1
        hits += min(k * bs, r["input_length"])
        for h in r["hash_ids"]:
            if h in order:
                if policy == "LRU":
                    order.move_to_end(h)
                elif policy == "LFU":
                    freq[h] += 1
                continue
            if len(order) >= cap:
                if policy == "LFU":
                    v = min(order, key=lambda x: (freq[x], admit[x]))
                    del order[v]
                else:
                    v, _ = order.popitem(last=False)
                freq.pop(v, None)
                admit.pop(v, None)
                evictions += 1
            clock += 1
            order[h] = True
            freq[h] = 1
            admit[h] = clock
    return {"hit_tokens": hits, "hit_rate": round(hits / total, 6),
            "evictions": evictions, "final_cache_blocks": len(order)}


results = {p: {str(c): run(p, c) for c in cfg["capacities"]} for p in cfg["policies"]}
out = {"total_requests": len(trace), "total_prompt_tokens": total, "results": results}
json.dump(out, open("policy_comparison.json", "w"), indent=2)
EOF
python3 /tmp/solve_sweep.py
