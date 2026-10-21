import csv
import json
import os

import pytest

W = "/root/work"
OUT = os.path.join(W, "changes.json")
TARGET = "berkshire hathaway inc"
TAB = chr(9)


def read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f, delimiter=TAB))


def find_acc(q):
    accs = [r["ACCESSION_NUMBER"] for r in read(f"{W}/{q}/COVERPAGE.tsv")
            if r["FILINGMANAGER_NAME"].strip().lower() == TARGET]
    assert len(accs) == 1
    return accs[0]


def holdings(q, acc):
    h = {}
    for r in read(f"{W}/{q}/INFOTABLE.tsv"):
        if (r["ACCESSION_NUMBER"] == acc and r["SSHPRNAMTTYPE"].strip() == "SH"
                and (r["PUTCALL"] or "").strip() == ""):
            h[r["CUSIP"]] = h.get(r["CUSIP"], 0) + int(r["VALUE"])
    return h


@pytest.fixture(scope="module")
def expected():
    a2, a3 = find_acc("2025-q2"), find_acc("2025-q3")
    h2, h3 = holdings("2025-q2", a2), holdings("2025-q3", a3)
    new = sorted([c for c in h3 if c not in h2], key=lambda c: (-h3[c], c))
    ex = sorted([c for c in h2 if c not in h3], key=lambda c: (-h2[c], c))
    d = {c: h3[c] - h2[c] for c in h3 if c in h2 and h3[c] > h2[c]}
    top = sorted(d, key=lambda c: (-d[c], c))[:3]
    return {"q2_accession": a2, "q3_accession": a3,
            "q2_stock_value": sum(h2.values()), "q3_stock_value": sum(h3.values()),
            "new_positions": new, "exited_positions": ex, "top_increases": top}


@pytest.fixture(scope="module")
def out():
    assert os.path.isfile(OUT)
    with open(OUT) as f:
        return json.load(f)


def test_output_exists():
    assert os.path.isfile(OUT)


def test_schema(out):
    for k in ["q2_accession", "q3_accession", "q2_stock_value", "q3_stock_value",
              "new_positions", "exited_positions", "top_increases"]:
        assert k in out, k
    for k in ["new_positions", "exited_positions", "top_increases"]:
        assert isinstance(out[k], list)
        assert all(isinstance(x, str) for x in out[k])


def test_accessions(out, expected):
    assert out["q2_accession"] == expected["q2_accession"]
    assert out["q3_accession"] == expected["q3_accession"]


def test_totals(out, expected):
    assert abs(float(out["q2_stock_value"]) - expected["q2_stock_value"]) < 0.5
    assert abs(float(out["q3_stock_value"]) - expected["q3_stock_value"]) < 0.5


def test_new_and_exited(out, expected):
    assert out["new_positions"] == expected["new_positions"]
    assert out["exited_positions"] == expected["exited_positions"]


def test_top_increases(out, expected):
    assert out["top_increases"] == expected["top_increases"]
