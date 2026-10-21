import json
import os
from collections import Counter

import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "adjacency.json")
STRAT = {"IRON", "COAL", "HORSES", "NITER", "OIL", "ALUMINUM", "URANIUM"}
KEYS = ["CAMPUS", "HOLY_SITE", "INDUSTRIAL_ZONE"]


def nbrs(x, y):
    if y % 2 == 0:
        d = [(1, 0), (-1, 0), (-1, -1), (0, -1), (-1, 1), (0, 1)]
    else:
        d = [(1, 0), (-1, 0), (0, -1), (1, -1), (0, 1), (1, 1)]
    return [(x + a, y + b) for a, b in d]


def expected():
    m = json.load(open(os.path.join(WORK, "map.json")))
    layouts = json.load(open(os.path.join(WORK, "layouts.json")))
    grid = {(t["x"], t["y"]): t for t in m["tiles"]}
    res = []
    for L in layouts:
        occ = {tuple(L["city_center"])} | {tuple(v) for v in L["districts"].values()}
        b = {}
        for d, p in L["districts"].items():
            c = Counter()
            for q in nbrs(*p):
                t = grid.get(q)
                if t is None:
                    continue
                o = q in occ
                if o:
                    c["DIST"] += 1
                if t["terrain"] == "MOUNTAIN":
                    c["MTN"] += 1
                f = t["feature"]
                if o and f in ("WOODS", "RAINFOREST"):
                    f = None
                if f:
                    c[f] += 1
                imp = None if o else t["improvement"]
                if imp:
                    c[imp] += 1
                if t["resource"] in STRAT:
                    c["STRAT"] += 1
            if d == "CAMPUS":
                v = 2 * c["GEOTHERMAL_FISSURE"] + 2 * c["REEF"] + c["MTN"] + c["RAINFOREST"] // 2 + c["DIST"] // 2
            elif d == "HOLY_SITE":
                v = c["MTN"] + c["WOODS"] // 2 + c["DIST"] // 2
            else:
                v = c["QUARRY"] + c["STRAT"] + c["MINE"] // 2 + c["LUMBER_MILL"] // 2 + c["DIST"] // 2
            b[d] = v
        res.append((L["id"], b))
    return res


@pytest.fixture(scope="module")
def out():
    assert os.path.exists(OUT), "adjacency.json missing"
    with open(OUT) as f:
        return json.load(f)


def test_file_exists():
    assert os.path.exists(OUT)


def test_schema(out):
    assert isinstance(out, dict)
    assert isinstance(out.get("layouts"), list)
    assert "grand_total" in out
    for L in out["layouts"]:
        assert set(L.keys()) >= {"id", "bonuses", "total"}
        assert set(L["bonuses"].keys()) == set(KEYS)


def test_ids_in_order(out):
    exp = expected()
    assert [L["id"] for L in out["layouts"]] == [e[0] for e in exp]


def test_bonuses(out):
    exp = expected()
    for L, (lid, b) in zip(out["layouts"], exp):
        for k in KEYS:
            assert int(L["bonuses"][k]) == b[k] and float(L["bonuses"][k]) == b[k], (lid, k, L["bonuses"][k], b[k])


def test_totals(out):
    exp = expected()
    grand = 0
    for L, (lid, b) in zip(out["layouts"], exp):
        assert float(L["total"]) == sum(b.values()), lid
        grand += sum(b.values())
    assert float(out["grand_total"]) == grand
