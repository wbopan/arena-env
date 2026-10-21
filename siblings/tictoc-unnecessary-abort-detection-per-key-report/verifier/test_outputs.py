import bisect
import csv
import json
import os

WORK = "/root/work"
OUT = os.path.join(WORK, "abort_report.csv")


def expected():
    writes, aborts = {}, []
    with open(os.path.join(WORK, "trace.jsonl")) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            if e["ev"] == "write":
                writes.setdefault(e["key"], []).append(e["wts"])
            else:
                aborts.append(e)
    for k in writes:
        writes[k].sort()
    res = {}
    for e in aborts:
        lst = writes.get(e["key"], [])
        i = bisect.bisect_right(lst, e["local_wts"])
        unn = i < len(lst) and e["commit_ts"] < lst[i]
        t, u = res.get(e["key"], (0, 0))
        res[e["key"]] = (t + 1, u + (1 if unn else 0))
    return res


def rows():
    with open(OUT, newline="") as f:
        return list(csv.DictReader(f))


def test_exists():
    assert os.path.exists(OUT)


def test_header():
    with open(OUT, newline="") as f:
        header = next(csv.reader(f))
    assert [h.strip() for h in header] == ["key", "total_aborts", "unnecessary_aborts", "rate"]


def test_keys_sorted():
    exp = expected()
    keys = [r["key"].strip() for r in rows()]
    assert keys == sorted(exp.keys())


def test_counts():
    exp = expected()
    for r in rows():
        t, u = exp[r["key"].strip()]
        assert int(r["total_aborts"]) == t, r
        assert int(r["unnecessary_aborts"]) == u, r


def test_rate():
    exp = expected()
    assert sum(u for _, u in exp.values()) > 0
    for r in rows():
        t, u = exp[r["key"].strip()]
        assert abs(float(r["rate"]) - u / t) <= 1e-4 + 1e-9, r
