import os
import random
from collections import deque

random.seed(7177)

DOMAIN = """(define (domain TPP-Propositional)
(:requirements :strips :typing)
(:types place locatable level - object
        depot market - place
        truck goods - locatable)
(:predicates (loaded ?g - goods ?t - truck ?l - level)
             (ready-to-load ?g - goods ?m - market ?l - level)
             (stored ?g - goods ?l - level)
             (on-sale ?g - goods ?m - market ?l - level)
             (next ?l1 ?l2 - level)
             (at ?t - truck ?p - place)
             (connected ?p1 ?p2 - place))
(:action drive
 :parameters (?t - truck ?from ?to - place)
 :precondition (and (at ?t ?from) (connected ?from ?to))
 :effect (and (not (at ?t ?from)) (at ?t ?to)))
(:action load
 :parameters (?g - goods ?t - truck ?m - market ?l1 ?l2 ?l3 ?l4 - level)
 :precondition (and (at ?t ?m) (loaded ?g ?t ?l3)
                    (ready-to-load ?g ?m ?l2) (next ?l2 ?l1) (next ?l4 ?l3))
 :effect (and (loaded ?g ?t ?l4) (not (loaded ?g ?t ?l3))
              (ready-to-load ?g ?m ?l1) (not (ready-to-load ?g ?m ?l2))))
(:action unload
 :parameters (?g - goods ?t - truck ?d - depot ?l1 ?l2 ?l3 ?l4 - level)
 :precondition (and (at ?t ?d) (loaded ?g ?t ?l2)
                    (stored ?g ?l3) (next ?l2 ?l1) (next ?l4 ?l3))
 :effect (and (loaded ?g ?t ?l1) (not (loaded ?g ?t ?l2))
              (stored ?g ?l4) (not (stored ?g ?l3))))
(:action buy
 :parameters (?t - truck ?g - goods ?m - market ?l1 ?l2 ?l3 ?l4 - level)
 :precondition (and (at ?t ?m) (on-sale ?g ?m ?l2) (ready-to-load ?g ?m ?l3)
                    (next ?l2 ?l1) (next ?l4 ?l3))
 :effect (and (on-sale ?g ?m ?l1) (not (on-sale ?g ?m ?l2))
              (ready-to-load ?g ?m ?l4) (not (ready-to-load ?g ?m ?l3))))
)
"""

markets = [f"market{i}" for i in range(1, 5)]
places = ["depot1"] + markets
goods = [f"goods{i}" for i in range(1, 4)]
adj = {p: set() for p in places}


def link(a, b):
    adj[a].add(b)
    adj[b].add(a)


for i in range(len(places)):
    link(places[i], places[(i + 1) % len(places)])
chords = [(a, b) for i, a in enumerate(places) for b in places[i + 1:] if b not in adj[a]]
for a, b in random.sample(chords, 1):
    link(a, b)

supply = {}
demand = {}
for g in goods:
    while True:
        s = {m: random.choice([0, 0, 1, 2, 3]) for m in markets}
        if sum(s.values()) >= 2:
            break
    for m in markets:
        supply[(g, m)] = s[m]
    demand[g] = random.randint(2, min(4, sum(s.values())))

lines = ["(define (problem tpp-check)", " (:domain TPP-Propositional)", " (:objects"]
lines.append("  " + " ".join(goods) + " - goods")
lines.append("  truck1 - truck")
lines.append("  " + " ".join(markets) + " - market")
lines.append("  depot1 - depot")
lines.append("  " + " ".join(f"level{i}" for i in range(7)) + " - level)")
lines.append(" (:init")
for i in range(6):
    lines.append(f"  (next level{i + 1} level{i})")
for a in places:
    for b in sorted(adj[a]):
        lines.append(f"  (connected {a} {b})")
lines.append("  (at truck1 depot1)")
for g in goods:
    for m in markets:
        lines.append(f"  (on-sale {g} {m} level{supply[(g, m)]})")
        lines.append(f"  (ready-to-load {g} {m} level0)")
    lines.append(f"  (loaded {g} truck1 level0)")
    lines.append(f"  (stored {g} level0)")
lines.append(" )")
lines.append(" (:goal (and")
for g in goods:
    lines.append(f"  (stored {g} level{demand[g]})")
lines.append(" ))")
lines.append(")")

with open("domain.pddl", "w") as f:
    f.write(DOMAIN)
with open("problem.pddl", "w") as f:
    f.write("\n".join(lines) + "\n")


def path(a, b):
    prev = {a: None}
    q = deque([a])
    while q:
        x = q.popleft()
        for y in sorted(adj[x]):
            if y not in prev:
                prev[y] = x
                q.append(y)
    out = []
    x = b
    while x != a:
        out.append(x)
        x = prev[x]
    return out[::-1]


def build(gorder, morder):
    pos = "depot1"
    acts = []
    onsale = dict(supply)
    for g in gorder:
        need = demand[g]
        loaded = 0
        for m in morder:
            while need > 0 and onsale[(g, m)] > 0:
                if pos != m:
                    for st in path(pos, m):
                        acts.append(f"drive(truck1, {pos}, {st})")
                        pos = st
                q = onsale[(g, m)]
                acts.append(f"buy(truck1, {g}, {m}, level{q - 1}, level{q}, level0, level1)")
                onsale[(g, m)] -= 1
                acts.append(f"load({g}, truck1, {m}, level0, level1, level{loaded}, level{loaded + 1})")
                loaded += 1
                need -= 1
        if pos != "depot1":
            for st in path(pos, "depot1"):
                acts.append(f"drive(truck1, {pos}, {st})")
                pos = st
        stored = 0
        while loaded > 0:
            acts.append(f"unload({g}, truck1, depot1, level{loaded - 1}, level{loaded}, level{stored}, level{stored + 1})")
            loaded -= 1
            stored += 1
    return acts


def args(line):
    return line[line.index("(") + 1:-1].split(", ")


P = build(goods, markets)
Q = build(goods[::-1], markets[::-1])
variants = [list(P), P[:-1]]

cands = []
for i, l in enumerate(P):
    if l.startswith("drive("):
        _, fr, to = args(l)
        bad = sorted(set(places) - adj[fr] - {fr})
        if bad:
            cands.append((i, fr, bad))
i, fr, bad = random.choice(cands)
v = list(P)
v[i] = f"drive(truck1, {fr}, {random.choice(bad)})"
variants.append(v)

buys = [i for i, l in enumerate(P) if l.startswith("buy(")]
i = random.choice(buys)
a = args(P[i])
a[3], a[4] = a[4], a[3]
v = list(P)
v[i] = "buy(" + ", ".join(a) + ")"
variants.append(v)

v = list(P)
i = random.randint(len(P) // 3, 2 * len(P) // 3)
v[i] = v[i].replace("truck1", "truck2")
variants.append(v)

loads = [i for i, l in enumerate(P) if l.startswith("load(")]
i = random.choice(loads)
v = list(P)
v[i] = "pick-up(" + v[i][5:]
variants.append(v)

i = random.choice(buys)
v = list(P)
v[i], v[i + 1] = v[i + 1], v[i]
variants.append(v)

variants.append(Q[:5] + [""] + Q[5:] + [""])

n = sorted(adj["depot1"])[0]
variants.append(P + [f"drive(truck1, depot1, {n})", f"drive(truck1, {n}, depot1)"])

variants.append(P[:random.randint(3, len(P) - 3)])

random.shuffle(variants)
os.makedirs("plans", exist_ok=True)
for k, v in enumerate(variants, 1):
    with open(os.path.join("plans", f"plan_{k:02d}.txt"), "w") as f:
        f.write("\n".join(v) + "\n")
