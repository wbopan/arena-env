#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import json, re
from pypdf import PdfReader

def lines_of(p):
    r = PdfReader(p)
    txt = "\n".join((pg.extract_text() or "") for pg in r.pages)
    return [l.strip() for l in txt.splitlines() if l.strip()]

out = {}
for name in ["paper1.pdf", "paper2.pdf", "paper3.pdf"]:
    L = lines_of(name)
    k = L.index("References")
    pre, post = L[:k], L[k + 1:]
    authors = re.findall(r"([A-Z][a-z]+ [A-Z][a-z]+) \[[0-9,]+\]", pre[1])
    ab = pre.index("Abstract")
    affs = sorted((int(m.group(1)), m.group(2).strip()) for m in (re.match(r"^\[(\d+)\] (.+)$", l) for l in pre[:ab]) if m)
    txt = "\n".join(pre)
    emails = sorted({e.lower() for e in re.findall(r"[A-Za-z0-9._-]+@[A-Za-z0-9.-]+\.[A-Za-z]+", txt)})
    arx = sorted(set(re.findall(r"arXiv:(\d{4}\.\d{4,5})", txt)))
    keys = {"%s, %s." % (a.split()[1], a.split()[0][0]) for a in authors}
    sc = []
    for l in post:
        m = re.match(r"^\[(\d+)\] (.+?) \(\d{4}\)\.", l)
        if m and keys & {x.strip() for x in m.group(2).split(";")}:
            sc.append(int(m.group(1)))
    out[name] = {"authors": authors, "affiliations": [a for _, a in affs], "emails": emails, "arxiv_ids": arx, "self_citations": sorted(sc)}

with open("leaks.json", "w") as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
EOF
python3 /tmp/solve.py
