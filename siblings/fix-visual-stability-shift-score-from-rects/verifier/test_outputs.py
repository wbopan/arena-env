import csv
import json
import os

import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "shift_scores.csv")
HEADER = ["id", "impact_fraction", "distance_fraction", "score"]


def _clip(r, W, H):
    return (max(r["x"], 0), max(r["y"], 0), min(r["x"] + r["width"], W), min(r["y"] + r["height"], H))


def _area(b):
    return max(0, b[2] - b[0]) * max(0, b[3] - b[1])


def expected():
    with open(os.path.join(WORK, "frames.json")) as f:
        d = json.load(f)
    W, H = d["viewport"]["width"], d["viewport"]["height"]
    out = {}
    for fr in d["frames"]:
        a = _clip(fr["previous"], W, H)
        b = _clip(fr["current"], W, H)
        inter = (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))
        union = _area(a) + _area(b) - _area(inter)
        imp = union / (W * H)
        dist = max(abs(fr["current"]["x"] - fr["previous"]["x"]), abs(fr["current"]["y"] - fr["previous"]["y"]))
        df = min(1.0, dist / max(W, H))
        out[fr["id"]] = (imp, df, imp * df)
    return out


def body():
    with open(OUT, newline="") as f:
        r = list(csv.reader(f))
    return r[0], [x for x in r[1:] if x]


def test_exists():
    assert os.path.isfile(OUT)


def test_header():
    h, _ = body()
    assert [c.strip() for c in h] == HEADER


def test_ids_sorted_complete():
    _, rows = body()
    assert [r[0].strip() for r in rows] == sorted(expected().keys())


def test_impact_and_distance():
    exp = expected()
    _, rows = body()
    for r in rows:
        e = exp[r[0].strip()]
        assert float(r[1]) == pytest.approx(e[0], abs=2e-6), r
        assert float(r[2]) == pytest.approx(e[1], abs=2e-6), r


def test_scores():
    exp = expected()
    _, rows = body()
    for r in rows:
        assert float(r[3]) == pytest.approx(exp[r[0].strip()][2], abs=2e-6), r
