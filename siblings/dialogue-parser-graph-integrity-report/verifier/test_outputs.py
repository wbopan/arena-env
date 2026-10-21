import json
import os
from collections import deque
from functools import lru_cache
import pytest

OUT = "/root/work/report.json"
SRC = "/root/work/dialogue.json"


def expected():
    g = json.load(open(SRC))
    ids = [n["id"] for n in g["nodes"]]
    idset = set(ids)
    start = ids[0]
    adj = {i: [] for i in ids}
    for e in g["edges"]:
        adj.setdefault(e["from"], []).append(e["to"])
    seen = {start}
    q = deque([start])
    dist = {start: 0}
    best = -1
    while q:
        u = q.popleft()
        for t in adj.get(u, []):
            if t == "End":
                if best == -1 or dist[u] + 1 < best:
                    best = dist[u] + 1
            elif t in idset and t not in seen:
                seen.add(t)
                dist[t] = dist[u] + 1
                q.append(t)

    @lru_cache(maxsize=None)
    def cnt(v):
        s = 0
        for t in adj.get(v, []):
            if t == "End":
                s += 1
            elif t in idset:
                s += cnt(t)
        return s

    missing = sorted({e["to"] for e in g["edges"] if e["to"] != "End" and e["to"] not in idset})
    return {
        "start": start,
        "reachable_count": len(seen),
        "unreachable": sorted(i for i in ids if i not in seen),
        "missing_targets": missing,
        "dead_ends": sorted(i for i in ids if not adj.get(i)),
        "paths_to_end": cnt(start),
        "shortest_to_end": best,
    }


@pytest.fixture(scope="module")
def rep():
    assert os.path.exists(OUT), "report.json missing"
    return json.load(open(OUT))


@pytest.fixture(scope="module")
def exp():
    return expected()


def test_keys(rep):
    for k in ["start", "reachable_count", "unreachable", "missing_targets", "dead_ends", "paths_to_end", "shortest_to_end"]:
        assert k in rep, f"missing key {k}"


def test_reachability(rep, exp):
    assert rep["start"] == exp["start"]
    assert rep["reachable_count"] == exp["reachable_count"]
    assert rep["unreachable"] == exp["unreachable"]


def test_missing_and_dead(rep, exp):
    assert rep["missing_targets"] == exp["missing_targets"]
    assert rep["dead_ends"] == exp["dead_ends"]


def test_paths(rep, exp):
    assert int(rep["paths_to_end"]) == exp["paths_to_end"]


def test_shortest(rep, exp):
    assert int(rep["shortest_to_end"]) == exp["shortest_to_end"]
