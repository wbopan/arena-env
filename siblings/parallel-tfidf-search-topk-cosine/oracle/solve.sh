#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import json, math, re
from collections import Counter

def tok(s):
    return re.findall(r"[a-z0-9]+", s.lower())

docs = [json.loads(l) for l in open("corpus.jsonl") if l.strip()]
N = len(docs)
df = Counter()
parsed = []
for d in docs:
    t = tok(d["text"])
    c = Counter(t)
    df.update(c.keys())
    parsed.append((d["doc_id"], c, len(t)))
idf = {w: math.log((1 + N) / (1 + k)) + 1 for w, k in df.items()}
vecs = []
for did, c, L in parsed:
    v = {w: (k / L) * idf[w] for w, k in c.items()}
    n = math.sqrt(sum(x * x for x in v.values()))
    vecs.append((did, {w: x / n for w, x in v.items()}))
out = {}
for q in json.load(open("queries.json")):
    t = tok(q["text"])
    c = Counter(t)
    qv = {w: (k / len(t)) * idf[w] for w, k in c.items() if w in idf}
    n = math.sqrt(sum(x * x for x in qv.values()))
    scores = []
    if n > 0:
        qv = {w: x / n for w, x in qv.items()}
        for did, dv in vecs:
            s = sum(x * dv[w] for w, x in qv.items() if w in dv)
            if s > 0:
                scores.append((did, s))
    scores.sort(key=lambda kv: (-kv[1], kv[0]))
    out[q["qid"]] = [{"doc_id": d, "score": round(s, 6)} for d, s in scores[:5]]
json.dump(out, open("results.json", "w"), indent=1)
EOF
python3 /tmp/solve.py
