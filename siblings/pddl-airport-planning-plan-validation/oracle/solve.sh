#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import glob, json, os, re

def tok(text):
    t = " ".join(l.split(";", 1)[0] for l in text.splitlines()).lower()
    return t.replace("(", " ( ").replace(")", " ) ").split()

def sexp(ts):
    st = [[]]
    for t in ts:
        if t == "(": st.append([])
        elif t == ")":
            x = st.pop(); st[-1].append(x)
        else: st[-1].append(t)
    return st[0][0]

def typed(l):
    out, pend, i = [], [], 0
    while i < len(l):
        if l[i] == "-":
            out += [(n, l[i+1]) for n in pend]; pend = []; i += 2
        else:
            pend.append(l[i]); i += 1
    return out + [(n, "object") for n in pend]

def conj(e):
    if not e: return []
    return list(e[1:]) if e[0] == "and" else [e]

dom = sexp(tok(open("domain.pddl").read()))
acts = {}
for it in dom:
    if isinstance(it, list) and it and it[0] == ":action":
        kv = {it[k]: it[k+1] for k in range(2, len(it)-1, 2)}
        eff = conj(kv.get(":effect", []))
        acts[it[1]] = (typed(kv.get(":parameters", [])),
                       [tuple(x) for x in conj(kv.get(":precondition", []))],
                       [tuple(e) for e in eff if e[0] != "not"],
                       [tuple(e[1]) for e in eff if e[0] == "not"])
prob = sexp(tok(open("problem.pddl").read()))
objs, init, goal = {}, set(), []
for it in prob:
    if isinstance(it, list) and it:
        if it[0] == ":objects": objs = dict(typed(it[1:]))
        elif it[0] == ":init": init = {tuple(x) for x in it[1:]}
        elif it[0] == ":goal": goal = [tuple(x) for x in conj(it[1])]

def run(lines):
    state = set(init); step = 0
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith(";"): continue
        step += 1
        reason = None
        m = re.match(r"^([\w-]+)\s*\((.*)\)$", line)
        if not m:
            reason = "invalid_action"
        else:
            name = m.group(1).lower(); s = m.group(2).strip()
            args = [a.strip().lower() for a in s.split(",")] if s else []
            if name not in acts:
                reason = "invalid_action"
            else:
                params, pre, add, dele = acts[name]
                if len(args) != len(params) or any(a not in objs or objs[a] != t for a, (_, t) in zip(args, params)):
                    reason = "invalid_action"
                else:
                    sub = {p: a for (p, _), a in zip(params, args)}
                    g = lambda at: tuple([at[0]] + [sub.get(x, x) for x in at[1:]])
                    if not all(g(x) in state for x in pre):
                        reason = "precondition"
                    else:
                        state = (state - {g(x) for x in dele}) | {g(x) for x in add}
        if reason:
            return {"valid": False, "failed_step": step, "reason": reason, "goals_satisfied": sum(x in state for x in goal)}
    gs = sum(x in state for x in goal)
    if gs == len(goal):
        return {"valid": True, "failed_step": None, "reason": None, "goals_satisfied": gs}
    return {"valid": False, "failed_step": None, "reason": "goal", "goals_satisfied": gs}

res = {}
for p in sorted(glob.glob("plans/plan_*.txt")):
    res[os.path.basename(p)] = run(open(p).read().splitlines())
json.dump(res, open("validation.json", "w"), indent=2)
EOF
python3 /tmp/solve.py
