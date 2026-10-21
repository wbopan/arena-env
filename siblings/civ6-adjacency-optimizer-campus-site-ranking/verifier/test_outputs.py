import csv
import json
import os

import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "campus_sites.csv")
BLOCK = {"IRON", "COAL", "HORSES", "NITER", "OIL", "ALUMINUM", "URANIUM", "SILK", "WINE", "DIAMONDS"}


def nbrs(x, y):
    if y % 2 == 0:
        d = [(1, 0), (-1, 0), (-1, -1), (0, -1), (-1, 1), (0, 1)]
    else:
        d = [(1, 0), (-1, 0), (0, -1), (1, -1), (0, 1), (1, 1)]
    return [(x + a, y + b) for a, b in d]


def hdist(p, q):
    def cube(x, y):
        cx = x - (y - (y & 1)) // 2
        return cx, -cx - y, y
    a, b = cube(*p), cube(*q)
    return sum(abs(i - j) for i, j in zip(a, b)) // 2


def expected():
    m = json.load(open(os.path.join(WORK, "map.json")))
    c = tuple(json.load(open(os.path.join(WORK, "city.json")))["city_center"])
    grid = {(t["x"], t["y"]): t for t in m["tiles"]}
    rows = []
    for p, t in grid.items():
        d = hdist(p, c)
        if not (1 <= d <= 3):
            continue
        if t["terrain"] not in ("GRASS", "PLAINS") or t["feature"] == "GEOTHERMAL_FISSURE" or t["resource"] in BLOCK:
            continue
        fis = reef = mtn = rf = wd = dist = 0
        for q in nbrs(*p):
            n = grid.get(q)
            if n is None:
                continue
            f = n["feature"]
            if q == c:
                dist += 1
                if f in ("WOODS", "RAINFOREST"):
                    f = None
            if n["terrain"] == "MOUNTAIN":
                mtn += 1
            fis += f == "GEOTHERMAL_FISSURE"
            reef += f == "REEF"
            rf += f == "RAINFOREST"
            wd += f == "WOODS"
        campus = 2 * fis + 2 * reef + mtn + rf // 2 + dist // 2
        holy = mtn + wd // 2 + dist // 2
        rows.append((p[0], p[1], d, campus, holy))
    rows.sort(key=lambda r: (-r[3], -r[4], r[1], r[0]))
    return rows


@pytest.fixture(scope="module")
def got():
    assert os.path.exists(OUT), "campus_sites.csv missing"
    with open(OUT, newline="") as f:
        rd = csv.reader(f)
        header = [h.strip() for h in next(rd)]
        rows = [tuple(int(float(v)) for v in r) for r in rd if r and any(v.strip() for v in r)]
    return header, rows


def test_file_exists():
    assert os.path.exists(OUT)


def test_header(got):
    assert got[0] == ["x", "y", "distance", "campus", "holy_site"]


def test_site_set(got):
    exp = {(r[0], r[1]) for r in expected()}
    have = [(r[0], r[1]) for r in got[1]]
    assert len(have) == len(set(have)), "duplicate sites"
    assert set(have) == exp


def test_values(got):
    exp = {(r[0], r[1]): r for r in expected()}
    for r in got[1]:
        assert r == exp[(r[0], r[1])], (r, exp.get((r[0], r[1])))


def test_order(got):
    assert got[1] == expected()
