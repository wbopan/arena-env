import csv
import json
import os

import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "cls_report.csv")
HEADER = ["url", "cls", "rating", "windows", "max_window_start_ms"]


def expected():
    with open(os.path.join(WORK, "shifts.json")) as f:
        data = json.load(f)
    res = []
    for p in data["pages"]:
        es = sorted((e for e in p["entries"] if not e["hadRecentInput"]), key=lambda e: e["startTime"])
        wins = []
        last = None
        for e in es:
            t = e["startTime"]
            if not wins or t - last > 1000 or t - wins[-1][0] > 5000:
                wins.append([t, 0.0])
            wins[-1][1] += e["value"]
            last = t
        if wins:
            best = max(w[1] for w in wins)
            start = next(w[0] for w in wins if w[1] == best)
        else:
            best, start = 0.0, None
        rating = "good" if best < 0.1 else ("needs-improvement" if best <= 0.25 else "poor")
        res.append((p["url"], best, rating, len(wins), start))
    return res


def rows():
    with open(OUT, newline="") as f:
        return list(csv.reader(f))


def test_exists():
    assert os.path.isfile(OUT)


def test_header_and_order():
    r = rows()
    assert [c.strip() for c in r[0]] == HEADER
    body = [x for x in r[1:] if x]
    assert [x[0].strip() for x in body] == [e[0] for e in expected()]


def test_cls_values():
    body = [x for x in rows()[1:] if x]
    for row, e in zip(body, expected()):
        assert float(row[1]) == pytest.approx(e[1], abs=1e-4), row


def test_ratings():
    body = [x for x in rows()[1:] if x]
    for row, e in zip(body, expected()):
        assert row[2].strip() == e[2], row


def test_windows_and_start():
    body = [x for x in rows()[1:] if x]
    for row, e in zip(body, expected()):
        assert int(row[3]) == e[3], row
        if e[4] is None:
            assert row[4].strip() == "", row
        else:
            assert float(row[4]) == pytest.approx(e[4], abs=1e-6), row
