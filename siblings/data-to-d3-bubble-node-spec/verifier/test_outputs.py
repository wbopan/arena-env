import csv
import json
import math
import os

import pytest

W = "/root/work"
OUT = os.path.join(W, "bubbles.json")
PAL = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]


def fmt(v):
    for div, s in ((1e12, "T"), (1e9, "B"), (1e6, "M")):
        if v >= div:
            m = v / div
            dec = 3 - len(str(int(m)))
            return f"{m:.{dec}f}{s}"
    return str(v)


def expected():
    with open(os.path.join(W, "data", "stock-descriptions.csv"), newline="") as fh:
        rows = list(csv.DictReader(fh))
    secs = sorted({r["sector"] for r in rows if r["sector"] != "ETF"})
    if any(r["sector"] == "ETF" for r in rows):
        secs.append("ETF")
    color = {s: PAL[i % 10] for i, s in enumerate(secs)}
    mx = max(int(r["marketCap"]) for r in rows if r["sector"] != "ETF")
    nodes = []
    for r in rows:
        etf = r["sector"] == "ETF"
        cap = None if etf else int(r["marketCap"])
        nodes.append({
            "ticker": r["ticker"], "name": r["name"], "sector": r["sector"],
            "marketCap": cap,
            "marketCapLabel": "" if etf else fmt(cap),
            "radius": 10.0 if etf else round(6 + 34 * math.sqrt(cap / mx), 2),
            "color": color[r["sector"]],
            "tooltip": not etf,
        })
    order = {s: i for i, s in enumerate(secs)}
    nodes.sort(key=lambda n: (order[n["sector"]], -(n["marketCap"] or 0), n["ticker"]))
    legend = [{"sector": s, "color": color[s]} for s in secs]
    return legend, nodes


@pytest.fixture(scope="module")
def out():
    assert os.path.exists(OUT), "bubbles.json missing"
    with open(OUT) as fh:
        return json.load(fh)


def test_structure(out):
    assert isinstance(out, dict)
    assert isinstance(out.get("legend"), list)
    assert isinstance(out.get("nodes"), list)
    keys = {"ticker", "name", "sector", "marketCap", "marketCapLabel", "radius", "color", "tooltip"}
    for n in out["nodes"]:
        assert keys <= set(n.keys()), f"missing keys in {n}"


def test_legend(out):
    legend, _ = expected()
    got = [(d["sector"], str(d["color"]).lower()) for d in out["legend"]]
    assert got == [(d["sector"], d["color"]) for d in legend]


def test_node_order(out):
    _, nodes = expected()
    assert [n["ticker"] for n in out["nodes"]] == [n["ticker"] for n in nodes]


def test_node_fields(out):
    _, nodes = expected()
    got = {n["ticker"]: n for n in out["nodes"]}
    for e in nodes:
        g = got[e["ticker"]]
        assert g["name"] == e["name"] and g["sector"] == e["sector"]
        if e["marketCap"] is None:
            assert g["marketCap"] is None, e["ticker"]
        else:
            assert g["marketCap"] == e["marketCap"], e["ticker"]
        assert g["marketCapLabel"] == e["marketCapLabel"], (e["ticker"], g["marketCapLabel"], e["marketCapLabel"])
        assert str(g["color"]).lower() == e["color"], e["ticker"]
        assert g["tooltip"] is e["tooltip"], e["ticker"]


def test_radius(out):
    _, nodes = expected()
    got = {n["ticker"]: n for n in out["nodes"]}
    for e in nodes:
        assert abs(float(got[e["ticker"]]["radius"]) - e["radius"]) <= 0.011, e["ticker"]
