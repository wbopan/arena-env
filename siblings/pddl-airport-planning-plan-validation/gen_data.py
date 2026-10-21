import os
import random
from collections import deque

random.seed(7321)

DOMAIN = """(define (domain airport-lite)
  (:requirements :strips :typing)
  (:types airplane segment)
  (:predicates (at ?a - airplane ?s - segment) (free ?s - segment)
               (connected ?s1 - segment ?s2 - segment) (runway ?s - segment)
               (parking ?s - segment) (airborne ?a - airplane) (parked ?a - airplane))
  ; taxi along a directed connection into a free segment
  (:action move
    :parameters (?a - airplane ?from - segment ?to - segment)
    :precondition (and (at ?a ?from) (connected ?from ?to) (free ?to))
    :effect (and (not (at ?a ?from)) (free ?from) (at ?a ?to) (not (free ?to))))
  (:action takeoff
    :parameters (?a - airplane ?s - segment)
    :precondition (and (at ?a ?s) (runway ?s))
    :effect (and (not (at ?a ?s)) (free ?s) (airborne ?a)))
  (:action park
    :parameters (?a - airplane ?s - segment)
    :precondition (and (at ?a ?s) (parking ?s))
    :effect (and (parked ?a)))
)
"""

PLANES = ["a1", "a2", "a3"]


def build():
    n = 14
    segs = [f"s{i}" for i in range(1, n + 1)]
    edges = set()
    for i in range(1, n):
        j = random.randrange(0, i)
        a, b = segs[i], segs[j]
        if random.random() < 0.15:
            edges.add((a, b) if random.random() < 0.5 else (b, a))
        else:
            edges.add((a, b))
            edges.add((b, a))
    for _ in range(4):
        a, b = random.sample(segs, 2)
        edges.add((a, b))
        edges.add((b, a))
    sh = segs[:]
    random.shuffle(sh)
    return segs, sorted(edges), sh[:2], sh[2:5], sh[5:8]


def successors(state, edges, runways, parking):
    pos, parked = state
    occ = {p for p in pos if p is not None}
    for i, a in enumerate(PLANES):
        s = pos[i]
        if s is None:
            continue
        for (x, y) in edges:
            if x == s and y not in occ:
                np_ = list(pos)
                np_[i] = y
                yield ("move", (a, s, y)), (tuple(np_), parked)
        if s in runways:
            np_ = list(pos)
            np_[i] = None
            yield ("takeoff", (a, s)), (tuple(np_), parked)
        if s in parking and not parked[i]:
            pk = list(parked)
            pk[i] = True
            yield ("park", (a, s)), (pos, tuple(pk))


def bfs(starts, edges, runways, parking, gp):
    start = (tuple(starts), (False, False, False))
    prev = {start: None}
    dq = deque([start])
    while dq:
        st = dq.popleft()
        pos, pk = st
        if pos[0] is None and pos[1] is None and pos[2] == gp and pk[2]:
            plan = []
            while prev[st] is not None:
                act, p = prev[st]
                plan.append(act)
                st = p
            return plan[::-1]
        for act, nst in successors(st, edges, runways, parking):
            if nst not in prev:
                prev[nst] = (act, st)
                dq.append(nst)
    return None


while True:
    segs, edges, runways, parking, starts = build()
    gp = parking[0]
    sol = bfs(starts, edges, runways, parking, gp)
    if sol and len(sol) >= 6:
        break

init = []
for a, s in zip(PLANES, starts):
    init.append(f"(at {a} {s})")
for s in segs:
    if s not in starts:
        init.append(f"(free {s})")
for x, y in edges:
    init.append(f"(connected {x} {y})")
for r in runways:
    init.append(f"(runway {r})")
for p in parking:
    init.append(f"(parking {p})")

problem = "(define (problem airport-lite-p1)\n  (:domain airport-lite)\n"
problem += "  (:objects " + " ".join(PLANES) + " - airplane " + " ".join(segs) + " - segment)\n"
problem += "  (:init\n    " + "\n    ".join(init) + ")\n"
problem += f"  (:goal (and (airborne a1) (airborne a2) (at a3 {gp}) (parked a3))))\n"

with open("domain.pddl", "w") as f:
    f.write(DOMAIN)
with open("problem.pddl", "w") as f:
    f.write(problem)

L = len(sol)
plans = []
plans.append(list(sol))
plans.append(sol[:-1])
k = random.randrange(1, L - 1)
plans.append(sol[:k] + sol[k + 1:])
k = random.randrange(0, L - 1)
p = list(sol)
p[k], p[k + 1] = p[k + 1], p[k]
plans.append(p)
k = random.randrange(0, L)
p = list(sol)
p[k] = ("taxi", p[k][1])
plans.append(p)
moves = [i for i, s in enumerate(sol) if s[0] == "move"]
k = random.choice(moves)
p = list(sol)
args = list(p[k][1])
args[1] = random.choice([x for x in PLANES if x != args[0]])
p[k] = ("move", tuple(args))
plans.append(p)
detour = None
es = set(edges)
for i, a in enumerate(PLANES):
    s = starts[i]
    for (x, y) in edges:
        if x == s and (y, x) in es and y not in starts:
            detour = [("move", (a, s, y)), ("move", (a, y, s))] + list(sol)
            break
    if detour:
        break
if detour is None:
    detour = list(sol) + [("park", ("a3", gp))]
plans.append(detour)
plans.append(list(sol) + [("takeoff", ("a3", gp))])

random.shuffle(plans)
os.makedirs("plans", exist_ok=True)
for idx, pl in enumerate(plans, 1):
    with open(os.path.join("plans", f"plan_{idx:02d}.txt"), "w") as f:
        f.write(f"; candidate plan {idx}\n")
        for name, args in pl:
            f.write(f"{name}({', '.join(args)})\n")
