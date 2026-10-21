import csv
import os

import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "meal_options.csv")
STATE = "Ohio"
CUISINES = ["American", "Chinese", "Italian", "Mediterranean"]
HEADER = ["city", "cuisine", "restaurant", "average_cost", "aggregate_rating"]


def _expected():
    cities = set()
    with open(os.path.join(WORK, "cities.txt")) as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) == 2 and parts[0].strip() == STATE:
                cities.add(parts[1].strip())
    with open(os.path.join(WORK, "restaurants.csv"), newline="") as f:
        rest = list(csv.DictReader(f))
    out = []
    for c in sorted(cities):
        for cu in sorted(CUISINES):
            cands = [r for r in rest
                     if r["City"] == c
                     and cu in [x.strip() for x in r["Cuisines"].split(",")]
                     and float(r["Average Cost"]) <= 60]
            if cands:
                b = min(cands, key=lambda r: (-float(r["Aggregate Rating"]), float(r["Average Cost"]), r["Name"]))
                out.append((c, cu, b["Name"], int(float(b["Average Cost"])), float(b["Aggregate Rating"])))
            else:
                out.append((c, cu, "-", 0, 0.0))
    return out


@pytest.fixture(scope="module")
def rows():
    assert os.path.exists(OUT), f"{OUT} not found"
    with open(OUT, newline="") as f:
        data = [[x.strip() for x in r] for r in csv.reader(f) if r]
    return data


def test_header(rows):
    assert rows[0] == HEADER, f"bad header {rows[0]}"


def test_pairs_and_order(rows):
    exp = _expected()
    got = [(r[0], r[1]) for r in rows[1:]]
    assert got == [(e[0], e[1]) for e in exp]


def test_restaurants(rows):
    exp = _expected()
    body = rows[1:]
    assert len(body) == len(exp)
    for r, e in zip(body, exp):
        assert r[2] == e[2], f"{e[0]}/{e[1]}: expected {e[2]}, got {r[2]}"


def test_numeric_values(rows):
    exp = _expected()
    body = rows[1:]
    assert len(body) == len(exp)
    for r, e in zip(body, exp):
        assert abs(float(r[3]) - e[3]) < 1e-6, f"{e[0]}/{e[1]} cost"
        assert abs(float(r[4]) - e[4]) < 0.01, f"{e[0]}/{e[1]} rating"
