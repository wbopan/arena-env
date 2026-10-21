import json
import os
import re

import pytest

SRC = "/root/work/src"
OUT = "/root/work/migration_report.json"
PREFIXES = ["javax.persistence", "javax.validation", "javax.servlet", "javax.transaction",
            "javax.ws.rs", "javax.mail", "javax.jms", "javax.xml.bind"]
ANNOT = {"javax.annotation.PostConstruct", "javax.annotation.PreDestroy",
         "javax.annotation.Resource", "javax.annotation.Priority"}
IMPORT_RE = re.compile(r"^\s*import\s+(?:static\s+)?([^;\s]+)\s*;")


def target_of(name):
    if name.startswith("javax.transaction.xa."):
        return None
    if name in ANNOT:
        return "jakarta.annotation"
    for p in PREFIXES:
        if name.startswith(p + "."):
            return p.replace("javax", "jakarta", 1)
    return None


def expected():
    scanned = 0
    per = {}
    bypkg = {}
    kept = set()
    for root, _d, files in os.walk(SRC):
        for fn in files:
            if not fn.endswith(".java"):
                continue
            scanned += 1
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, SRC).replace(os.sep, "/")
            n = 0
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    m = IMPORT_RE.match(line)
                    if not m:
                        continue
                    name = m.group(1)
                    t = target_of(name)
                    if t:
                        n += 1
                        bypkg[t] = bypkg.get(t, 0) + 1
                    elif name.startswith("javax."):
                        kept.add(name)
            if n:
                per[rel] = n
    return {
        "files_scanned": scanned,
        "files_changed": len(per),
        "total_migrated_imports": sum(per.values()),
        "by_package": bypkg,
        "per_file": per,
        "retained_javax": sorted(kept),
    }


@pytest.fixture(scope="module")
def report():
    assert os.path.exists(OUT), "migration_report.json missing"
    with open(OUT) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def exp():
    return expected()


def test_schema(report):
    for k in ["files_scanned", "files_changed", "total_migrated_imports",
              "by_package", "per_file", "retained_javax"]:
        assert k in report, f"missing key {k}"


def test_counts(report, exp):
    assert report["files_scanned"] == exp["files_scanned"]
    assert report["files_changed"] == exp["files_changed"]
    assert report["total_migrated_imports"] == exp["total_migrated_imports"]


def test_by_package(report, exp):
    got = {k: v for k, v in report["by_package"].items() if v}
    assert got == exp["by_package"]


def test_per_file(report, exp):
    assert report["per_file"] == exp["per_file"]


def test_retained(report, exp):
    assert report["retained_javax"] == exp["retained_javax"]
