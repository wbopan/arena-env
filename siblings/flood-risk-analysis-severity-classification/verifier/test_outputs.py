import csv
import json
import os

import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "flood_severity.json")


def _num(x):
    x = (x or "").strip()
    if not x:
        return None
    v = float(x)
    if v == -9999:
        return None
    return v


def expected():
    daily = {}
    with open(os.path.join(WORK, "gage_height_iv.rdb")) as f:
        lines = [l.rstrip("\n") for l in f if not l.startswith("#") and l.strip()]
    cols = lines[0].split("\t")
    ci = {c: i for i, c in enumerate(cols)}
    for l in lines[2:]:
        p = l.split("\t")
        while len(p) < len(cols):
            p.append("")
        v = p[ci["00065"]].strip()
        if not v:
            continue
        s = p[ci["site_no"]].strip()
        d = p[ci["datetime"]].strip()[:10]
        dd = daily.setdefault(s, {})
        v = float(v)
        if d not in dd or v > dd[d]:
            dd[d] = v
    thr = {}
    with open(os.path.join(WORK, "nws_thresholds.csv"), newline="") as f:
        r = csv.reader(f)
        h = next(r)
        for row in r:
            m = dict(zip(h, row[: len(h)]))
            thr[m["usgs id"].strip()] = m
    res = {}
    for s in sorted(daily):
        if s not in thr:
            continue
        t = thr[s]
        fl = _num(t["flood stage"])
        if fl is None:
            continue
        dd = daily[s]
        peak = max(dd.values())
        pdate = min(d for d, v in dd.items() if v == peak)
        sev = "normal"
        for name, key in [("major", "major flood stage"), ("moderate", "moderate flood stage"), ("minor", "flood stage"), ("action", "action stage")]:
            tv = _num(t[key])
            if tv is not None and peak >= tv:
                sev = name
                break
        res[s] = {"peak_stage_ft": round(peak, 2), "peak_date": pdate, "severity": sev, "flood_days": sum(1 for v in dd.values() if v >= fl)}
    return res


@pytest.fixture(scope="module")
def out():
    assert os.path.exists(OUT), "output file missing"
    with open(OUT) as f:
        data = json.load(f)
    return data


def test_exists():
    assert os.path.exists(OUT)


def test_schema(out):
    assert isinstance(out, dict) and isinstance(out.get("stations"), list)
    for e in out["stations"]:
        for k in ["station_id", "peak_stage_ft", "peak_date", "severity", "flood_days"]:
            assert k in e, k
        assert isinstance(e["station_id"], str) and len(e["station_id"]) == 8


def test_station_set_and_order(out):
    exp = expected()
    ids = [e["station_id"] for e in out["stations"]]
    assert ids == sorted(exp.keys())


def test_peaks(out):
    exp = expected()
    for e in out["stations"]:
        x = exp[e["station_id"]]
        assert abs(float(e["peak_stage_ft"]) - x["peak_stage_ft"]) <= 0.006, e
        assert e["peak_date"] == x["peak_date"], e


def test_severity(out):
    exp = expected()
    for e in out["stations"]:
        assert e["severity"] == exp[e["station_id"]]["severity"], e


def test_flood_days(out):
    exp = expected()
    for e in out["stations"]:
        assert int(e["flood_days"]) == exp[e["station_id"]]["flood_days"], e
