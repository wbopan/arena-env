import csv
import json
import re
from pathlib import Path

import pytest

WORK = Path("/root/work")
OUT = WORK / "audit.json"
VALID = {"missing_doi", "unknown_doi", "title_mismatch", "year_mismatch"}
PREFIXES = ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "http://dx.doi.org/", "doi:")


def _clean(v):
    v = v.strip()
    if v.endswith(","):
        v = v[:-1].strip()
    if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
        v = v[1:-1]
    return v.replace("{", "").replace("}", "").strip()


def _parse(path):
    entries = []
    cur = None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*@(\w+)\s*\{\s*([^,\s]+)\s*,", line)
        if m:
            cur = {"key": m.group(2), "f": {}}
            entries.append(cur)
            continue
        if cur is None:
            continue
        if re.match(r"^\s*\}\s*$", line):
            cur = None
            continue
        m = re.match(r"^\s*([A-Za-z_]+)\s*=\s*(.*)$", line)
        if m:
            cur["f"][m.group(1).lower()] = _clean(m.group(2))
    return entries


def _ndoi(d):
    d = d.strip().lower()
    for p in PREFIXES:
        if d.startswith(p):
            d = d[len(p):]
            break
    return d.strip()


def _nt(t):
    t = t.replace("\\", "").replace("{", "").replace("}", "").lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def _expected():
    reg = {}
    with open(WORK / "registry.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            reg[_ndoi(r["doi"])] = r
    res = {}
    for e in _parse(WORK / "refs.bib"):
        d = _ndoi(e["f"].get("doi", ""))
        if not d:
            res[e["key"]] = "missing_doi"
        elif d not in reg:
            res[e["key"]] = "unknown_doi"
        elif _nt(e["f"].get("title", "")) != _nt(reg[d]["title"]):
            res[e["key"]] = "title_mismatch"
        elif e["f"].get("year", "").strip() != reg[d]["year"].strip():
            res[e["key"]] = "year_mismatch"
    return res


@pytest.fixture(scope="module")
def data():
    assert OUT.exists(), "audit.json not found"
    return json.loads(OUT.read_text())


def test_file_exists():
    assert OUT.exists(), "audit.json not found"


def test_schema(data):
    assert isinstance(data, dict)
    assert isinstance(data.get("fake_keys"), list)
    assert isinstance(data.get("reasons"), dict)
    assert all(isinstance(k, str) for k in data["fake_keys"])
    assert all(v in VALID for v in data["reasons"].values())


def test_sorted(data):
    assert data["fake_keys"] == sorted(data["fake_keys"])


def test_fake_keys(data):
    exp = _expected()
    assert sorted(data["fake_keys"]) == sorted(exp)


def test_reasons(data):
    exp = _expected()
    assert data["reasons"] == exp
