import csv
import os

import pytest

W = "/root/work/2025-q3"
OUT = "/root/work/top_holders.csv"
TAB = chr(9)
HEADER = ["rank", "manager_name", "accession_number", "value", "pct_of_portfolio"]


def read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f, delimiter=TAB))


@pytest.fixture(scope="module")
def expected():
    names = {r["ACCESSION_NUMBER"]: r["FILINGMANAGER_NAME"].strip() for r in read(f"{W}/COVERPAGE.tsv")}
    info = read(f"{W}/INFOTABLE.tsv")
    cus = {r["CUSIP"] for r in info if "palantir" in r["NAMEOFISSUER"].lower()}
    assert len(cus) == 1
    cusip = cus.pop()
    total, pos = {}, {}
    for r in info:
        a = r["ACCESSION_NUMBER"]
        v = int(r["VALUE"])
        total[a] = total.get(a, 0) + v
        if r["CUSIP"] == cusip and r["SSHPRNAMTTYPE"].strip() == "SH" and (r["PUTCALL"] or "").strip() == "":
            pos[a] = pos.get(a, 0) + v
    ranked = sorted([a for a in pos if pos[a] > 0], key=lambda a: (-pos[a], a))[:5]
    return [{"rank": i + 1, "manager_name": names[a], "accession_number": a,
             "value": pos[a], "pct": round(100 * pos[a] / total[a], 2)}
            for i, a in enumerate(ranked)]


@pytest.fixture(scope="module")
def rows():
    assert os.path.isfile(OUT)
    with open(OUT, newline="") as f:
        return list(csv.reader(f))


def test_output_exists():
    assert os.path.isfile(OUT)


def test_header_and_count(rows):
    assert [h.strip() for h in rows[0]] == HEADER
    data = [r for r in rows[1:] if any(x.strip() for x in r)]
    assert len(data) == 5


def test_ranking_identity(rows, expected):
    data = [r for r in rows[1:] if any(x.strip() for x in r)]
    for r, e in zip(data, expected):
        assert int(float(r[0])) == e["rank"]
        assert r[2].strip() == e["accession_number"]
        assert r[1].strip().lower() == e["manager_name"].lower()


def test_values(rows, expected):
    data = [r for r in rows[1:] if any(x.strip() for x in r)]
    for r, e in zip(data, expected):
        assert abs(float(r[3]) - e["value"]) < 0.5


def test_pct_of_portfolio(rows, expected):
    data = [r for r in rows[1:] if any(x.strip() for x in r)]
    for r, e in zip(data, expected):
        assert abs(float(r[4]) - e["pct"]) <= 0.011
