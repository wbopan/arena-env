import csv
import json
import math
import os

import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "lab_summary.json")
TOL = 0.011

CONV = {
    "Creatinine": {"mg/dl": 1.0, "umol/l": 1 / 88.4},
    "BUN": {"mg/dl": 1.0, "mmol/l": 2.8},
    "Hemoglobin": {"g/dl": 1.0, "g/l": 0.1, "mmol/l": 1.611},
    "Calcium": {"mg/dl": 1.0, "mmol/l": 4.0, "meq/l": 2.0},
    "Glucose": {"mg/dl": 1.0, "mmol/l": 18.016},
    "Albumin": {"g/dl": 1.0, "g/l": 0.1},
}


def norm_unit(u):
    return u.strip().lower().replace("\u00b5", "u").replace("\u03bc", "u")


@pytest.fixture(scope="module")
def exp():
    dropped = 0
    vals = {a: [] for a in CONV}
    with open(os.path.join(WORK, "measurements.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            a = r["analyte"].strip()
            u = norm_unit(r["unit"])
            s = r["value"].strip().replace(",", ".")
            try:
                v = float(s)
            except ValueError:
                v = None
            if v is None or not math.isfinite(v) or a not in CONV or u not in CONV[a]:
                dropped += 1
                continue
            vals[a].append(v * CONV[a][u])
    stats = {a: {"n": len(x), "mean": sum(x) / len(x), "min": min(x), "max": max(x)}
             for a, x in vals.items()}
    return dropped, stats


@pytest.fixture(scope="module")
def got():
    assert os.path.exists(OUT), "output missing"
    with open(OUT) as f:
        return json.load(f)


def test_file_is_json(got):
    assert isinstance(got, dict)
    assert "dropped_rows" in got and "analytes" in got


def test_dropped_rows(exp, got):
    assert int(got["dropped_rows"]) == exp[0]


def test_analytes_and_counts(exp, got):
    assert set(got["analytes"].keys()) == set(CONV.keys())
    for a, st in exp[1].items():
        assert int(got["analytes"][a]["n"]) == st["n"], a


def test_means(exp, got):
    for a, st in exp[1].items():
        g = float(got["analytes"][a]["mean"])
        assert abs(g - st["mean"]) <= TOL, f"{a} mean: expected {st['mean']:.2f}, got {g}"


def test_min_max(exp, got):
    for a, st in exp[1].items():
        for k in ("min", "max"):
            g = float(got["analytes"][a][k])
            assert abs(g - st[k]) <= TOL, f"{a} {k}: expected {st[k]:.2f}, got {g}"
