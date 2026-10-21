import csv
import json
import os

import pytest

W = "/root/work"
OUT = os.path.join(W, "report.json")


def _load(name):
    with open(os.path.join(W, name)) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def expected():
    reqs = _load("requests.json")
    cfg = _load("config.json")
    plan = _load("plan.json")
    with open(os.path.join(W, "t_matrix.csv")) as f:
        M = [[int(x) for x in row] for row in csv.reader(f) if row]
    depot = cfg["depot_node"]
    by_node = {}
    for rq in reqs:
        for tr in rq["trips"]:
            by_node[tr["pickup_node"]] = (tr, True)
            by_node[tr["dropoff_node"]] = (tr, False)
    routes = []
    served = set()
    for r in plan["routes"]:
        seq = r["node_sequence"]
        pos = {nd: i for i, nd in enumerate(seq)}
        ok = True
        t = r["start_time"]
        prev = depot
        load = 0
        mx = 0
        wait = 0
        ss = {}
        for nd in seq:
            tr, isp = by_node[nd]
            a = t + M[prev][nd]
            lo, hi = tr["pickup_tw"] if isp else tr["dropoff_tw"]
            s = max(a, lo)
            wait += s - a
            if s > hi:
                ok = False
            ss[nd] = s
            load += tr["load"] if isp else -tr["load"]
            mx = max(mx, load)
            if load > cfg["capacity"]:
                ok = False
            t = s + cfg["service_time"]
            prev = nd
        end = t + M[prev][depot] if seq else r["start_time"]
        if end - r["start_time"] > cfg["shift_duration"]:
            ok = False
        for nd in seq:
            tr, isp = by_node[nd]
            p, d = tr["pickup_node"], tr["dropoff_node"]
            if p not in pos or d not in pos or pos[p] > pos[d]:
                ok = False
            elif isp and ss[d] - ss[p] > cfg["max_ride_time"]:
                ok = False
        if ok:
            served.update(by_node[nd][0]["trip_id"] for nd in seq)
        routes.append({"vehicle_id": r["vehicle_id"], "feasible": ok, "end_time": end,
                       "max_load": mx, "total_wait": wait})
    sreq = []
    strips = []
    for rq in reqs:
        ids = [tr["trip_id"] for tr in rq["trips"]]
        if all(i in served for i in ids):
            sreq.append(rq["request_id"])
            strips.extend(ids)
    return {"routes": routes, "served_trips": sorted(strips), "served_requests": sorted(sreq)}


@pytest.fixture(scope="module")
def report():
    assert os.path.exists(OUT), "report.json missing"
    with open(OUT) as f:
        return json.load(f)


def test_exists(report):
    assert isinstance(report, dict)


def test_schema(report, expected):
    assert isinstance(report.get("routes"), list)
    assert len(report["routes"]) == len(expected["routes"])
    for r in report["routes"]:
        for k in ("vehicle_id", "feasible", "end_time", "max_load", "total_wait"):
            assert k in r, k
        assert isinstance(r["feasible"], bool)
    assert isinstance(report.get("served_trips"), list)
    assert isinstance(report.get("served_requests"), list)


def test_route_timing(report, expected):
    for got, exp in zip(report["routes"], expected["routes"]):
        assert got["vehicle_id"] == exp["vehicle_id"]
        assert int(got["end_time"]) == exp["end_time"], exp["vehicle_id"]
        assert int(got["total_wait"]) == exp["total_wait"], exp["vehicle_id"]


def test_route_feasibility_and_load(report, expected):
    for got, exp in zip(report["routes"], expected["routes"]):
        assert int(got["max_load"]) == exp["max_load"], exp["vehicle_id"]
        assert got["feasible"] == exp["feasible"], exp["vehicle_id"]


def test_served(report, expected):
    assert list(report["served_requests"]) == expected["served_requests"]
    assert list(report["served_trips"]) == expected["served_trips"]
