import os, json, csv

W = "/root/work"
OUT = os.path.join(W, "audit.json")
KEYS = {"makespan", "illegal_machine", "duration_mismatch", "precedence_violations",
        "machine_overlaps", "downtime_violations", "feasible"}


def parse_instance():
    with open(os.path.join(W, "instance.txt")) as f:
        tok = f.read().split()
    it = iter(tok)
    J = int(next(it)); int(next(it))
    jobs = []
    for _ in range(J):
        n = int(next(it)); ops = []
        for _ in range(n):
            k = int(next(it)); d = {}
            for _ in range(k):
                m = int(next(it)); p = int(next(it)); d[m] = p
            ops.append(d)
        jobs.append(ops)
    return jobs


def ov(a, b, c, d):
    return a < d and c < b


def expected():
    jobs = parse_instance()
    dt = {}
    with open(os.path.join(W, "downtime.csv")) as f:
        for r in csv.DictReader(f):
            dt.setdefault(int(r["machine"]), []).append((int(r["start"]), int(r["end"])))
    with open(os.path.join(W, "baseline_solution.json")) as f:
        rows = json.load(f)["schedule"]
    res = {"makespan": max(int(r["end"]) for r in rows)}
    ill = mis = 0
    for r in rows:
        al = jobs[r["job"]][r["op"]]
        if r["machine"] not in al:
            ill += 1
        elif r["end"] - r["start"] != al[r["machine"]]:
            mis += 1
    res["illegal_machine"] = ill
    res["duration_mismatch"] = mis
    bm = {(r["job"], r["op"]): r for r in rows}
    res["precedence_violations"] = sum(1 for (j, o), r in bm.items()
                                       if (j, o + 1) in bm and r["end"] > bm[(j, o + 1)]["start"])
    mo = 0
    for i in range(len(rows)):
        for k in range(i + 1, len(rows)):
            a, b = rows[i], rows[k]
            if a["machine"] == b["machine"] and ov(a["start"], a["end"], b["start"], b["end"]):
                mo += 1
    res["machine_overlaps"] = mo
    res["downtime_violations"] = sum(1 for r in rows if any(ov(r["start"], r["end"], s, e)
                                                           for s, e in dt.get(r["machine"], [])))
    res["feasible"] = all(res[k] == 0 for k in ("illegal_machine", "duration_mismatch",
                          "precedence_violations", "machine_overlaps", "downtime_violations"))
    return res


def load():
    with open(OUT) as f:
        return json.load(f)


def test_exists_and_json():
    assert os.path.exists(OUT)
    assert isinstance(load(), dict)


def test_schema():
    d = load()
    assert set(d.keys()) == KEYS
    assert isinstance(d["feasible"], bool)
    for k in KEYS - {"feasible"}:
        assert type(d[k]) is int, k


def test_makespan_and_feasible():
    d, e = load(), expected()
    assert d["makespan"] == e["makespan"]
    assert d["feasible"] == e["feasible"]


def test_machine_and_duration_counts():
    d, e = load(), expected()
    assert d["illegal_machine"] == e["illegal_machine"]
    assert d["duration_mismatch"] == e["duration_mismatch"]


def test_conflict_counts():
    d, e = load(), expected()
    assert d["precedence_violations"] == e["precedence_violations"]
    assert d["machine_overlaps"] == e["machine_overlaps"]
    assert d["downtime_violations"] == e["downtime_violations"]
