import csv
import os
import re

import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "harmonized.csv")
MISSING = {"", "na", "nan"}
TOL = 0.011


def parse(s):
    s = s.strip()
    if s.lower() in MISSING:
        return None
    return float(s.replace(",", "."))


def load_ref():
    ref = {}
    with open(os.path.join(WORK, "lab_reference.csv"), newline="") as f:
        for r in csv.DictReader(f):
            facs = [float(x) for x in r["alt_factors"].split(";") if x.strip()]
            ref[r["feature"]] = (float(r["min"]), float(r["max"]), facs)
    return ref


@pytest.fixture(scope="module")
def ref():
    return load_ref()


@pytest.fixture(scope="module")
def exp(ref):
    with open(os.path.join(WORK, "labs_wide.csv"), newline="") as f:
        rd = csv.reader(f)
        header = next(rd)
        rows = list(rd)
    out = []
    for r in rows:
        vals = [parse(c) for c in r[1:]]
        if any(v is None for v in vals):
            continue
        conv = []
        for col, v in zip(header[1:], vals):
            lo, hi, facs = ref[col]
            if not (lo <= v <= hi):
                for k in facs:
                    if lo <= v * k <= hi:
                        v = v * k
                        break
            conv.append(v)
        out.append((r[0].strip(), conv))
    return header, out


@pytest.fixture(scope="module")
def got():
    assert os.path.exists(OUT), "output file missing"
    with open(OUT, newline="") as f:
        rows = [r for r in csv.reader(f) if r]
    return rows[0], rows[1:]


def test_file_exists():
    assert os.path.isfile(OUT)


def test_header(exp, got):
    assert [h.strip() for h in got[0]] == [h.strip() for h in exp[0]]


def test_rows_kept(exp, got):
    assert [r[0].strip() for r in got[1]] == [pid for pid, _ in exp[1]]


def test_two_decimal_format(got):
    pat = re.compile(r"^-?\d+\.\d{2}$")
    for r in got[1]:
        for c in r[1:]:
            assert pat.match(c), f"bad format: {c!r}"


def test_values_in_range(ref, got):
    header = [h.strip() for h in got[0]]
    for r in got[1]:
        for col, c in zip(header[1:], r[1:]):
            lo, hi, _ = ref[col]
            v = float(c)
            assert lo - 0.006 <= v <= hi + 0.006, f"{r[0]} {col}={c} out of range"


def test_values_match(exp, got):
    header, erows = exp
    grows = got[1]
    assert len(grows) == len(erows)
    for (pid, ev), gr in zip(erows, grows):
        assert len(gr) == len(header)
        for col, e, g in zip(header[1:], ev, gr[1:]):
            assert abs(float(g) - e) <= TOL, f"{pid} {col}: expected {e:.2f}, got {g}"
