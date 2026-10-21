import glob
import json
import os
import re

import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "sorry_report.json")
DECL = re.compile(r"^(theorem|lemma|def) ([A-Za-z_][A-Za-z0-9_']*)")
TOK = re.compile(r"[A-Za-z_][A-Za-z0-9_']*")


def expected():
    decls = {}
    for path in sorted(glob.glob(os.path.join(WORK, "project", "*.lean"))):
        cur = None
        with open(path, encoding="utf-8") as fh:
            for line in fh.read().splitlines():
                m = DECL.match(line)
                if m:
                    cur = m.group(2)
                    decls[cur] = {"kind": m.group(1), "toks": set()}
                if cur is None:
                    continue
                code = line.split("--", 1)[0]
                decls[cur]["toks"].update(TOK.findall(code))
    direct = {n for n, d in decls.items() if "sorry" in d["toks"]}
    refs = {n: {t for t in d["toks"] if t in decls and t != n} for n, d in decls.items()}
    tainted = set(direct)
    changed = True
    while changed:
        changed = False
        for n in decls:
            if n not in tainted and refs[n] & tainted:
                tainted.add(n)
                changed = True
    clean = sorted(n for n, d in decls.items() if d["kind"] in ("theorem", "lemma") and n not in tainted)
    return {"declarations": len(decls), "direct": sorted(direct), "tainted": sorted(tainted), "clean_theorems": clean}


@pytest.fixture(scope="module")
def report():
    assert os.path.exists(OUT), "sorry_report.json missing"
    with open(OUT, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def exp():
    return expected()


def test_file_exists():
    assert os.path.exists(OUT)


def test_schema(report):
    assert isinstance(report, dict)
    for key in ("declarations", "direct", "tainted", "clean_theorems"):
        assert key in report, key
    assert isinstance(report["declarations"], int)
    for key in ("direct", "tainted", "clean_theorems"):
        assert isinstance(report[key], list)
        assert all(isinstance(x, str) for x in report[key])
        assert report[key] == sorted(report[key]), key + " not sorted"


def test_declaration_count(report, exp):
    assert report["declarations"] == exp["declarations"]


def test_direct(report, exp):
    assert report["direct"] == exp["direct"]


def test_tainted(report, exp):
    assert report["tainted"] == exp["tainted"]


def test_clean_theorems(report, exp):
    assert report["clean_theorems"] == exp["clean_theorems"]
