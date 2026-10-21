#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import glob
import json
import os
import re

LINE = re.compile(r"^\s*([\w-]+)\s*\(([^()]*)\)\s*$")


def sexp(text):
    text = re.sub(r";[^\n]*", "", text).lower()
    toks = text.replace("(", " ( ").replace(")", " ) ").split()
    st = [[]]
    for t in toks:
        if t == "(":
            st.append([])
        elif t == ")":
            x = st.pop()
            st[-1].append(x)
        else:
            st[-1].append(t)
    return st[0][0]


def conj(e):
    if not e:
        return []
    return e[1:] if e[0] == "and" else [e]


acts = {}
for item in sexp(open("domain.pddl").read()):
    if isinstance(item, list) and item and item[0] == ":action":
        kv = {item[i]: item[i + 1] for i in range(2, len(item) - 1, 2)}
        params = [p for p in kv[":parameters"] if p.startswith("?")]
        pre = [tuple(a) for a in conj(kv.get(":precondition", []))]
        add, dele = [], []
        for e in conj(kv.get(":effect", [])):
            if e[0] == "not":
                dele.append(tuple(e[1]))
            else:
                add.append(tuple(e))
        acts[item[1]] = (params, pre, add, dele)

objs, init, goal = set(), set(), []
for item in sexp(open("problem.pddl").read()):
    if isinstance(item, list) and item:
        if item[0] == ":objects":
            toks = item[1:]
            i = 0
            while i < len(toks):
                if toks[i] == "-":
                    i += 2
                else:
                    objs.add(toks[i])
                    i += 1
        elif item[0] == ":init":
            init = {tuple(a) for a in item[1:]}
        elif item[0] == ":goal":
            goal = [tuple(a) for a in conj(item[1])]


def run(path):
    lines = [l for l in open(path).read().splitlines() if l.strip()]
    state = set(init)
    for k, raw in enumerate(lines, 1):
        m = LINE.match(raw.lower())
        if not m:
            return len(lines), k, False
        name = m.group(1)
        args = [a.strip() for a in m.group(2).split(",") if a.strip()]
        if name not in acts:
            return len(lines), k, False
        params, pre, add, dele = acts[name]
        if len(args) != len(params) or any(a not in objs for a in args):
            return len(lines), k, False
        sub = dict(zip(params, args))
        g = lambda atom: tuple(sub.get(x, x) for x in atom)
        if not all(g(a) in state for a in pre):
            return len(lines), k, False
        state -= {g(a) for a in dele}
        state |= {g(a) for a in add}
    return len(lines), None, all(a in state for a in goal)


res = {}
for p in sorted(glob.glob("plans/*.txt")):
    pid = os.path.splitext(os.path.basename(p))[0]
    n, ff, gr = run(p)
    res[pid] = {"num_actions": n, "first_failure": ff, "goal_reached": gr}
out = {"plans": res, "valid_plans": sorted(k for k, v in res.items() if v["goal_reached"])}
with open("results.json", "w") as f:
    json.dump(out, f, indent=2)
EOF
python3 /tmp/solve.py
