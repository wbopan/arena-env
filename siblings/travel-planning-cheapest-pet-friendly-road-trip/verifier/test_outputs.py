import csv
import itertools
import json
import os

import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "trip.json")
STATE = "Ohio"
ORIGIN = "Minneapolis"
TOL = 0.01


def _state_cities():
    out = set()
    with open(os.path.join(WORK, "cities.txt")) as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) == 2 and parts[0].strip() == STATE:
                out.add(parts[1].strip())
    return out


def _accommodations():
    with open(os.path.join(WORK, "accommodations.csv"), newline="") as f:
        return {r["NAME"]: r for r in csv.DictReader(f)}


def _legs():
    with open(os.path.join(WORK, "distance.csv"), newline="") as f:
        return {(r["origin"], r["destination"]): float(r["cost"]) for r in csv.DictReader(f)}


def _ok(r):
    return ("No pets" not in r["house_rules"]
            and int(r["maximum occupancy"]) >= 2
            and int(r["minimum nights"]) <= 2)


def _expected_min():
    cities = _state_cities()
    cheapest = {}
    for r in _accommodations().values():
        if r["city"] in cities and _ok(r):
            p = 2 * float(r["price"])
            cheapest[r["city"]] = min(p, cheapest.get(r["city"], float("inf")))
    legs = _legs()
    best = None
    for perm in itertools.permutations(cheapest, 3):
        route = [ORIGIN, *perm, ORIGIN]
        hops = list(zip(route, route[1:]))
        if not all(h in legs for h in hops):
            continue
        total = sum(legs[h] for h in hops) + sum(cheapest[c] for c in perm)
        if best is None or total < best:
            best = total
    return best


@pytest.fixture(scope="module")
def payload():
    assert os.path.exists(OUT), f"{OUT} not found"
    with open(OUT) as f:
        return json.load(f)


def test_schema(payload):
    assert isinstance(payload, dict)
    for k in ["route", "accommodations", "driving_cost", "accommodation_cost", "total_cost"]:
        assert k in payload, f"missing key {k}"
    assert isinstance(payload["route"], list) and len(payload["route"]) == 5
    assert isinstance(payload["accommodations"], list) and len(payload["accommodations"]) == 3
    for k in ["driving_cost", "accommodation_cost", "total_cost"]:
        assert isinstance(payload[k], (int, float)) and not isinstance(payload[k], bool)


def test_route_valid(payload):
    route = payload["route"]
    assert route[0] == ORIGIN and route[-1] == ORIGIN
    mid = route[1:4]
    cities = _state_cities()
    assert len(set(mid)) == 3, "cities must be distinct"
    for c in mid:
        assert c in cities, f"{c} is not a {STATE} city"
    legs = _legs()
    for h in zip(route, route[1:]):
        assert tuple(h) in legs, f"leg {h} not drivable"


def test_accommodations_valid(payload):
    acc = _accommodations()
    for city, name in zip(payload["route"][1:4], payload["accommodations"]):
        assert name in acc, f"unknown accommodation {name}"
        r = acc[name]
        assert r["city"] == city, f"{name} is not in {city}"
        assert _ok(r), f"{name} violates constraints"


def test_costs_consistent(payload):
    legs = _legs()
    acc = _accommodations()
    route = payload["route"]
    drive = sum(legs[tuple(h)] for h in zip(route, route[1:]))
    accc = sum(2 * float(acc[n]["price"]) for n in payload["accommodations"])
    assert abs(payload["driving_cost"] - drive) <= TOL
    assert abs(payload["accommodation_cost"] - accc) <= TOL
    assert abs(payload["total_cost"] - (drive + accc)) <= TOL


def test_total_is_minimum(payload):
    exp = _expected_min()
    assert exp is not None
    assert abs(payload["total_cost"] - exp) <= TOL, f"expected minimum {exp}, got {payload['total_cost']}"
