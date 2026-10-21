import glob
import json
import os
import re

import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "validation.json")


def tokenize(text):
    lines = [l.split(";", 1)[0] for l in text.splitlines()]
    t = " ".join(lines).lower().replace("(", " ( ").replace(")", " ) ")
    return t.split()


def parse(tokens):
    stack = [[]]
    for tok in tokens:
        if tok == "(":
            stack.append([])
        elif tok == ")":
            x = stack.pop()
            stack[-1].append(x)
        else:
            stack[-1].append(tok)
    return stack[0][0]


def typed(lst):
    out, pending, i = [], [], 0
    while i < len(lst):
        if lst[i] == "-":
            out += [(n, lst[i + 1]) for n in pending]
            pending = []
            i += 2
        else:
            pending.append(lst[i])
            i += 1
    out += [(n, "object") for n in pending]
    return out


def conj(e):
    if not e:
        return []
    if e[0] == "and":
        return list(e[1:])
    return [e]


def load_domain(path):
    with open(path) as f:
        d = parse(tokenize(f.read()))
    acts = {}
    for item in d:
        if isinstance(item, list) and item and item[0] == ":action":
            kv = {}
            for k in range(2, len(item) - 1, 2):
                kv[item[k]] = item[k + 1]
            params = typed(kv.get(":parameters", []))
            pre = [tuple(x) for x in conj(kv.get(":precondition", []))]
            add, dele = [], []
            for e in conj(kv.get(":effect", [])):
                if e[0] == "not":
                    dele.append(tuple(e[1]))
                else:
                    add.append(tuple(e))
            acts[item[1]] = (params, pre, add, dele)
    return acts


def load_problem(path):
    with open(path) as f:
        p = parse(tokenize(f.read()))
    objs, init, goal = {}, set(), []
    for item in p:
        if isinstance(item, list) and item:
            if item[0] == ":objects":
                objs = dict(typed(item[1:]))
            elif item[0] == ":init":
                init = {tuple(x) for x in item[1:]}
            elif item[0] == ":goal":
                goal = [tuple(x) for x in conj(item[1])]
    return objs, init, goal


def check(acts, objs, init, goal, lines):
    state = set(init)
    step = 0
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith(";"):
            continue
        step += 1
        reason = None
        m = re.match(r"^([\w-]+)\s*\((.*)\)$", line)
        if not m:
            reason = "invalid_action"
        else:
            name = m.group(1).lower()
            s = m.group(2).strip()
            args = [a.strip().lower() for a in s.split(",")] if s else []
            if name not in acts:
                reason = "invalid_action"
            else:
                params, pre, add, dele = acts[name]
                if len(args) != len(params) or any(
                    a not in objs or objs[a] != t for a, (_, t) in zip(args, params)
                ):
                    reason = "invalid_action"
                else:
                    sub = {p: a for (p, _), a in zip(params, args)}

                    def g(at):
                        return tuple([at[0]] + [sub.get(x, x) for x in at[1:]])

                    if not all(g(x) in state for x in pre):
                        reason = "precondition"
                    else:
                        state = (state - {g(x) for x in dele}) | {g(x) for x in add}
        if reason:
            return {"valid": False, "failed_step": step, "reason": reason,
                    "goals_satisfied": sum(x in state for x in goal)}
    gs = sum(x in state for x in goal)
    if gs == len(goal):
        return {"valid": True, "failed_step": None, "reason": None, "goals_satisfied": gs}
    return {"valid": False, "failed_step": None, "reason": "goal", "goals_satisfied": gs}


def expected():
    acts = load_domain(os.path.join(WORK, "domain.pddl"))
    objs, init, goal = load_problem(os.path.join(WORK, "problem.pddl"))
    res = {}
    for p in sorted(glob.glob(os.path.join(WORK, "plans", "plan_*.txt"))):
        with open(p) as f:
            res[os.path.basename(p)] = check(acts, objs, init, goal, f.read().splitlines())
    return res


def load_out():
    with open(OUT) as f:
        return json.load(f)


def test_output_exists_and_json():
    assert os.path.exists(OUT)
    assert isinstance(load_out(), dict)


def test_keys_match_plan_files():
    assert set(load_out().keys()) == set(expected().keys())


def test_schema():
    out = load_out()
    for k, v in out.items():
        assert set(v.keys()) >= {"valid", "failed_step", "reason", "goals_satisfied"}, k
        assert isinstance(v["valid"], bool), k
        assert v["reason"] in (None, "invalid_action", "precondition", "goal"), k


def test_validity_flags():
    out, exp = load_out(), expected()
    for k, e in exp.items():
        assert out[k]["valid"] == e["valid"], k


def test_failed_step_and_reason():
    out, exp = load_out(), expected()
    for k, e in exp.items():
        assert out[k]["reason"] == e["reason"], k
        assert out[k]["failed_step"] == e["failed_step"], k


def test_goals_satisfied():
    out, exp = load_out(), expected()
    for k, e in exp.items():
        assert int(out[k]["goals_satisfied"]) == e["goals_satisfied"], k
