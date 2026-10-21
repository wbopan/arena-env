import glob
import json
import os
import re

import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "results.json")
LINE = re.compile(r"^\s*([\w-]+)\s*\(([^()]*)\)\s*$")


def sexp(text):
    text = re.sub(r";[^\n]*", "", text).lower()
    toks = text.replace("(", " ( ").replace(")", " ) ").split()
    stack = [[]]
    for t in toks:
        if t == "(":
            stack.append([])
        elif t == ")":
            x = stack.pop()
            stack[-1].append(x)
        else:
            stack[-1].append(t)
    return stack[0][0]


def conj(e):
    if not e:
        return []
    if e[0] == "and":
        return e[1:]
    return [e]


def load_domain():
    d = sexp(open(os.path.join(WORK, "domain.pddl")).read())
    acts = {}
    for item in d:
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
    return acts


def load_problem():
    p = sexp(open(os.path.join(WORK, "problem.pddl")).read())
    objs, init, goal = set(), set(), []
    for item in p:
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
    return objs, init, goal


def simulate(path, acts, objs, init, goal):
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

        def g(atom):
            return tuple(sub.get(x, x) for x in atom)

        if not all(g(a) in state for a in pre):
            return len(lines), k, False
        state -= {g(a) for a in dele}
        state |= {g(a) for a in add}
    return len(lines), None, all(a in state for a in goal)


@pytest.fixture(scope="module")
def expected():
    acts = load_domain()
    objs, init, goal = load_problem()
    res = {}
    for p in sorted(glob.glob(os.path.join(WORK, "plans", "*.txt"))):
        pid = os.path.splitext(os.path.basename(p))[0]
        n, ff, gr = simulate(p, acts, objs, init, goal)
        res[pid] = {"num_actions": n, "first_failure": ff, "goal_reached": gr}
    return res


@pytest.fixture(scope="module")
def output():
    with open(OUT) as f:
        return json.load(f)


def test_output_exists_and_is_json():
    assert os.path.isfile(OUT)
    with open(OUT) as f:
        data = json.load(f)
    assert isinstance(data, dict)


def test_schema(output, expected):
    assert "plans" in output and "valid_plans" in output
    assert set(output["plans"].keys()) == set(expected.keys())
    for pid, e in output["plans"].items():
        assert isinstance(e["num_actions"], int) and not isinstance(e["num_actions"], bool)
        ff = e["first_failure"]
        assert ff is None or (isinstance(ff, int) and not isinstance(ff, bool))
        assert isinstance(e["goal_reached"], bool)


def test_num_actions(output, expected):
    for pid, e in expected.items():
        assert output["plans"][pid]["num_actions"] == e["num_actions"], pid


def test_first_failure(output, expected):
    for pid, e in expected.items():
        assert output["plans"][pid]["first_failure"] == e["first_failure"], pid


def test_goal_reached(output, expected):
    for pid, e in expected.items():
        assert output["plans"][pid]["goal_reached"] == e["goal_reached"], pid


def test_valid_plans(output, expected):
    want = sorted(pid for pid, e in expected.items() if e["goal_reached"])
    assert output["valid_plans"] == want
