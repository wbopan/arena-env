import bisect
import json
import os

WORK = "/root/work"
OUT = os.path.join(WORK, "unnecessary_aborts.json")


def expected():
    wts = {}
    with open(os.path.join(WORK, "writes.tsv")) as f:
        for line in f:
            p = line.split()
            if len(p) < 4:
                continue
            wts.setdefault(int(p[1]), []).append(int(p[2]))
    for k in wts:
        wts[k].sort()
    status = {}
    with open(os.path.join(WORK, "aborts.tsv")) as f:
        for line in f:
            p = line.split()
            if len(p) < 6:
                continue
            txn, key, lw, cts = int(p[0]), int(p[1]), int(p[2]), int(p[4])
            lst = wts.get(key, [])
            i = bisect.bisect_right(lst, lw)
            unn = i < len(lst) and cts < lst[i]
            status[txn] = status.get(txn, True) and unn
    return sorted(t for t, v in status.items() if v)


def load():
    with open(OUT) as f:
        return json.load(f)


def test_exists():
    assert os.path.exists(OUT)


def test_int_array():
    d = load()
    assert isinstance(d, list)
    assert all(isinstance(x, int) and not isinstance(x, bool) for x in d)


def test_sorted_unique():
    d = load()
    assert d == sorted(d)
    assert len(d) == len(set(d))


def test_values():
    exp = expected()
    assert len(exp) > 0
    assert load() == exp
