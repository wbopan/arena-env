import csv
import re
from pathlib import Path

import pytest

WORK = Path("/root/work")
OUT = WORK / "missing_fields.csv"
REQ = {"article": ["author", "title", "journal", "year"],
       "inproceedings": ["author", "title", "booktitle", "year"],
       "book": ["author", "title", "publisher", "year"],
       "misc": ["author", "title", "year"]}


def _val(raw):
    v = raw.strip()
    if v.endswith(","):
        v = v[:-1].strip()
    if len(v) >= 2 and v.startswith('"') and v.endswith('"'):
        v = v[1:-1]
    return v.replace("{", "").replace("}", "").strip()


def _entries():
    res = []
    cur = None
    for line in (WORK / "library.bib").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*@(\w+)\s*\{\s*([^,\s]+)\s*,", line)
        if m:
            cur = [m.group(2), m.group(1).lower(), {}]
            res.append(cur)
            continue
        if cur is None:
            continue
        if re.match(r"^\s*\}\s*$", line):
            cur = None
            continue
        m = re.match(r"^\s*([A-Za-z_]+)\s*=\s*(.*)$", line)
        if m:
            cur[2][m.group(1).lower()] = _val(m.group(2))
    return res


def _expected():
    rows = []
    for key, et, fields in _entries():
        if et not in REQ:
            continue
        miss = []
        for fl in REQ[et]:
            v = fields.get(fl)
            ok = v is not None and v != ""
            if fl == "year":
                ok = ok and re.fullmatch(r"\d{4}", v) is not None
            if not ok:
                miss.append(fl)
        if miss:
            rows.append([key, et, ";".join(miss)])
    return sorted(rows, key=lambda r: r[0])


@pytest.fixture(scope="module")
def rows():
    assert OUT.exists(), "missing_fields.csv not found"
    with open(OUT, newline="", encoding="utf-8") as f:
        return [[c.strip() for c in r] for r in csv.reader(f) if r]


def test_file_exists():
    assert OUT.exists()


def test_header(rows):
    assert rows[0] == ["key", "entry_type", "missing_fields"]


def test_flagged_keys(rows):
    exp = _expected()
    assert sorted(r[0] for r in rows[1:]) == sorted(r[0] for r in exp)


def test_sorted(rows):
    ks = [r[0] for r in rows[1:]]
    assert ks == sorted(ks)


def test_rows_exact(rows):
    assert rows[1:] == _expected()
