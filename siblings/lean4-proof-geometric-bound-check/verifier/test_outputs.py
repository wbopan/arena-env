import csv
import os
from fractions import Fraction

import pytest

IN = "/root/work/sequences.csv"
OUT = "/root/work/bounds_report.csv"


def expected():
    res = []
    with open(IN, newline="") as fh:
        for row in csv.DictReader(fh):
            s0 = Fraction(row["s0"])
            a = Fraction(row["a"])
            r = Fraction(row["r"])
            b = Fraction(row["bound"])
            lim = s0 + a * r / (1 - r)
            holds = lim <= b
            fv = ""
            if not holds:
                n = 0
                power = Fraction(1)
                s = s0
                while s <= b:
                    n += 1
                    power *= r
                    s += a * power
                fv = str(n)
            res.append({"id": row["id"], "limit": lim, "holds": "true" if holds else "false", "first_violation": fv})
    return res


@pytest.fixture(scope="module")
def exp():
    return expected()


@pytest.fixture(scope="module")
def got():
    assert os.path.exists(OUT), "bounds_report.csv missing"
    with open(OUT, newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        rows = [r for r in reader if r]
    return header, rows


def test_file_exists():
    assert os.path.exists(OUT)


def test_header_and_rows(got, exp):
    header, rows = got
    assert [h.strip() for h in header] == ["id", "limit", "holds", "first_violation"]
    assert len(rows) == len(exp)
    assert [r[0].strip() for r in rows] == [e["id"] for e in exp]


def test_limits(got, exp):
    _, rows = got
    for r, e in zip(rows, exp):
        lim = e["limit"]
        assert r[1].strip() == f"{lim.numerator}/{lim.denominator}", (e["id"], r[1])


def test_holds(got, exp):
    _, rows = got
    for r, e in zip(rows, exp):
        assert r[2].strip() == e["holds"], e["id"]


def test_first_violation(got, exp):
    _, rows = got
    for r, e in zip(rows, exp):
        val = r[3].strip() if len(r) > 3 else ""
        assert val == e["first_violation"], (e["id"], val, e["first_violation"])
