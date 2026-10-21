import os, json, csv

W = "/root/work"
OUT = os.path.join(W, "repaired.csv")
HEADER = ["job", "op", "machine", "start", "end", "dur"]


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


def load_dt():
    dt = {}
    with open(os.path.join(W, "downtime.csv")) as f:
        for r in csv.DictReader(f):
            dt.setdefault(int(r["machine"]), []).append((int(r["start"]), int(r["end"])))
    return dt


def ov(a, b, c, d):
    return a < d and c < b


def expected():
    jobs = parse_instance()
    dt = load_dt()
    with open(os.path.join(W, "baseline_solution.json")) as f:
        base = json.load(f)["schedule"]
    bmap = {(r["job"], r["op"]): (i, r) for i, r in enumerate(base)}
    keys = sorted(bmap, key=lambda k: (k[1], bmap[k][1]["start"], bmap[k][0]))
    placed = {}
    new = {}
    for k in keys:
        j, o = k
        r = bmap[k][1]
        al = jobs[j][o]
        m = r["machine"]
        if m not in al:
            m = min(al, key=lambda x: (al[x], x))
        d = al[m]
        anchor = r["start"] if o == 0 else max(r["start"], new[(j, o - 1)][2])
        t = anchor
        busy = placed.get(m, []) + dt.get(m, [])
        while any(ov(t, t + d, a, b) for a, b in busy):
            t += 1
        placed.setdefault(m, []).append((t, t + d))
        new[k] = (m, t, t + d, d)
    return [[j, o] + list(new[(j, o)]) for (j, o) in sorted(new)]


def load_out():
    with open(OUT, newline="") as f:
        rows = [r for r in csv.reader(f) if r]
    return [c.strip() for c in rows[0]], [[int(float(c)) for c in r] for r in rows[1:]]


def test_exists_and_header():
    assert os.path.exists(OUT)
    h, _ = load_out()
    assert h == HEADER


def test_all_operations_once():
    _, rows = load_out()
    jobs = parse_instance()
    want = sorted((j, o) for j in range(len(jobs)) for o in range(len(jobs[j])))
    got = [(r[0], r[1]) for r in rows]
    assert sorted(got) == want and len(got) == len(set(got))


def test_legal_machines_and_durations():
    _, rows = load_out()
    jobs = parse_instance()
    for j, o, m, s, e, d in rows:
        assert m in jobs[j][o]
        assert d == jobs[j][o][m] and e == s + d


def test_feasible():
    _, rows = load_out()
    dt = load_dt()
    mp = {(r[0], r[1]): r for r in rows}
    for (j, o), r in mp.items():
        if (j, o + 1) in mp:
            assert r[4] <= mp[(j, o + 1)][3]
        for a, b in dt.get(r[2], []):
            assert not ov(r[3], r[4], a, b)
    for i in range(len(rows)):
        for k in range(i + 1, len(rows)):
            if rows[i][2] == rows[k][2]:
                assert not ov(rows[i][3], rows[i][4], rows[k][3], rows[k][4])


def test_matches_procedure_exactly():
    _, rows = load_out()
    assert rows == expected()
