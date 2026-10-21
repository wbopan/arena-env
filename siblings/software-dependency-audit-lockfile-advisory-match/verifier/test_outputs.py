import json
import os

W = "/root/work"
OUT = os.path.join(W, "audit.json")
SEVS = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]


def vt(x):
    return tuple(int(p) for p in x.split("."))


def sev(sc):
    if sc is None:
        return "UNKNOWN"
    if sc < 4.0:
        return "LOW"
    if sc < 7.0:
        return "MEDIUM"
    if sc < 9.0:
        return "HIGH"
    return "CRITICAL"


def expected():
    lock = json.load(open(os.path.join(W, "package-lock.json")))
    inst = set()
    for path, meta in lock["packages"].items():
        if not path:
            continue
        inst.add((path.rsplit("node_modules/", 1)[1], meta["version"]))
    advs = json.load(open(os.path.join(W, "advisories.json")))["advisories"]
    out = []
    for name, ver in inst:
        for a in advs:
            if a["package"] != name:
                continue
            hit = any(vt(r["introduced"]) <= vt(ver) and (r["fixed"] is None or vt(ver) < vt(r["fixed"]))
                      for r in a["ranges"])
            if hit:
                sc = a["cvss_v3"] if a["cvss_v3"] is not None else a["cvss_v2"]
                out.append({"package": name, "version": ver, "advisory": a["id"], "score": sc, "severity": sev(sc)})
    out.sort(key=lambda f: (f["package"], vt(f["version"]), f["advisory"]))
    return out


def load():
    with open(OUT) as f:
        return json.load(f)


def key(f):
    return (f["package"], f["version"], f["advisory"])


def test_exists_and_schema():
    d = load()
    assert isinstance(d.get("findings"), list)
    assert isinstance(d.get("summary"), dict)
    assert "affected_packages" in d
    for f in d["findings"]:
        assert set(["package", "version", "advisory", "score", "severity"]) <= set(f)


def test_finding_set():
    got = sorted(key(f) for f in load()["findings"])
    exp = sorted(key(f) for f in expected())
    assert got == exp


def test_scores_and_severity():
    got = {key(f): f for f in load()["findings"]}
    for e in expected():
        g = got[key(e)]
        if e["score"] is None:
            assert g["score"] is None
        else:
            assert g["score"] is not None and abs(float(g["score"]) - e["score"]) < 1e-6
        assert g["severity"] == e["severity"]


def test_order():
    assert [key(f) for f in load()["findings"]] == [key(f) for f in expected()]


def test_summary():
    d = load()
    exp = expected()
    want = {s: sum(1 for f in exp if f["severity"] == s) for s in SEVS}
    assert {s: d["summary"].get(s) for s in SEVS} == want
    assert d["affected_packages"] == len(set(f["package"] for f in exp))
