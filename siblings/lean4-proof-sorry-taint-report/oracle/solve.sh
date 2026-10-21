#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_taint.py << 'EOF'
import glob, json, os, re
DECL = re.compile(r"^(theorem|lemma|def) ([A-Za-z_][A-Za-z0-9_']*)")
TOK = re.compile(r"[A-Za-z_][A-Za-z0-9_']*")
kind = {}
toks = {}
for path in sorted(glob.glob("/root/work/project/*.lean")):
    cur = None
    for line in open(path, encoding="utf-8").read().splitlines():
        m = DECL.match(line)
        if m:
            cur = m.group(2)
            kind[cur] = m.group(1)
            toks[cur] = set()
        if cur is None:
            continue
        toks[cur].update(TOK.findall(line.split("--", 1)[0]))
direct = {n for n in toks if "sorry" in toks[n]}
rev = {n: set() for n in toks}
for n in toks:
    for t in toks[n]:
        if t in toks and t != n:
            rev[t].add(n)
tainted = set(direct)
stack = list(direct)
while stack:
    x = stack.pop()
    for y in rev[x]:
        if y not in tainted:
            tainted.add(y)
            stack.append(y)
clean = sorted(n for n in toks if kind[n] in ("theorem", "lemma") and n not in tainted)
out = {"declarations": len(toks), "direct": sorted(direct), "tainted": sorted(tainted), "clean_theorems": clean}
with open("/root/work/sorry_report.json", "w") as fh:
    json.dump(out, fh, indent=2)
EOF
python3 /tmp/solve_taint.py
