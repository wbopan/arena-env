import json
import os
import re

import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "fuzz_summary.json")
KEYS = {"final_cov", "final_ft", "final_corpus_units", "total_execs", "new_events", "crashed", "exception_type"}
STAT = re.compile(r"^#(\d+)\s+(\w+)\s+cov: (\d+) ft: (\d+) corp: (\d+)/")


def expected():
    res = {}
    d = os.path.join(WORK, "logs")
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".log"):
            continue
        lib = fn[:-4]
        with open(os.path.join(d, fn)) as f:
            lines = f.read().split("\n")
        stats = [m for m in (STAT.match(l) for l in lines) if m]
        last = stats[-1]
        crashed = False
        et = None
        for i, l in enumerate(lines):
            if l.strip() == "=== Uncaught Python exception: ===":
                crashed = True
                et = lines[i + 1].split(": ", 1)[0]
                break
        res[lib] = {
            "final_cov": int(last.group(3)),
            "final_ft": int(last.group(4)),
            "final_corpus_units": int(last.group(5)),
            "total_execs": max(int(m.group(1)) for m in stats),
            "new_events": sum(1 for m in stats if m.group(2) == "NEW"),
            "crashed": crashed,
            "exception_type": et,
        }
    return res


@pytest.fixture(scope="module")
def out():
    with open(OUT) as f:
        return json.load(f)


def test_file_exists():
    assert os.path.isfile(OUT)


def test_schema(out):
    exp = expected()
    assert isinstance(out, dict)
    assert set(out.keys()) == set(exp.keys())
    for lib, v in out.items():
        assert set(v.keys()) == KEYS, lib


def test_coverage_fields(out):
    exp = expected()
    for lib, e in exp.items():
        for k in ("final_cov", "final_ft", "final_corpus_units"):
            assert out[lib][k] == e[k], (lib, k)


def test_exec_and_new(out):
    exp = expected()
    for lib, e in exp.items():
        assert out[lib]["total_execs"] == e["total_execs"], lib
        assert out[lib]["new_events"] == e["new_events"], lib


def test_crash_fields(out):
    exp = expected()
    for lib, e in exp.items():
        assert out[lib]["crashed"] is e["crashed"], lib
        assert out[lib]["exception_type"] == e["exception_type"], lib
