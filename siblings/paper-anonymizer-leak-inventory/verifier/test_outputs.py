import json
import re
from pathlib import Path

import pytest
from pypdf import PdfReader

W = Path("/root/work")
OUT = W / "leaks.json"
PAPERS = ["paper1.pdf", "paper2.pdf", "paper3.pdf"]


def lines_of(p):
    r = PdfReader(str(p))
    txt = "\n".join((pg.extract_text() or "") for pg in r.pages)
    return [l.strip() for l in txt.splitlines() if l.strip()]


def expected(name):
    L = lines_of(W / name)
    k = L.index("References")
    pre, post = L[:k], L[k + 1:]
    authors = re.findall(r"([A-Z][a-z]+ [A-Z][a-z]+) \[[0-9,]+\]", pre[1])
    abs_i = pre.index("Abstract")
    affs = []
    for l in pre[:abs_i]:
        m = re.match(r"^\[(\d+)\] (.+)$", l)
        if m:
            affs.append((int(m.group(1)), m.group(2).strip()))
    affs = [a for _, a in sorted(affs)]
    txt = "\n".join(pre)
    emails = sorted({e.lower() for e in re.findall(r"[A-Za-z0-9._-]+@[A-Za-z0-9.-]+\.[A-Za-z]+", txt)})
    arx = sorted(set(re.findall(r"arXiv:(\d{4}\.\d{4,5})", txt)))
    keys = {"%s, %s." % (a.split()[1], a.split()[0][0]) for a in authors}
    selfc = []
    for l in post:
        m = re.match(r"^\[(\d+)\] (.+?) \(\d{4}\)\.", l)
        if m and keys & {x.strip() for x in m.group(2).split(";")}:
            selfc.append(int(m.group(1)))
    return {"authors": authors, "affiliations": affs, "emails": emails,
            "arxiv_ids": arx, "self_citations": sorted(selfc)}


EXP = {p: expected(p) for p in PAPERS}


def load():
    assert OUT.exists(), "leaks.json missing"
    return json.loads(OUT.read_text())


def test_file_and_schema():
    d = load()
    assert isinstance(d, dict)
    for p in PAPERS:
        assert p in d, p
        for f in ["authors", "affiliations", "emails", "arxiv_ids", "self_citations"]:
            assert f in d[p], (p, f)
            assert isinstance(d[p][f], list), (p, f)


def test_authors():
    d = load()
    for p in PAPERS:
        assert d[p]["authors"] == EXP[p]["authors"], p


def test_affiliations():
    d = load()
    for p in PAPERS:
        assert [str(x).strip() for x in d[p]["affiliations"]] == EXP[p]["affiliations"], p


def test_emails():
    d = load()
    for p in PAPERS:
        assert d[p]["emails"] == EXP[p]["emails"], p


def test_arxiv_ids():
    d = load()
    for p in PAPERS:
        assert d[p]["arxiv_ids"] == EXP[p]["arxiv_ids"], p


def test_self_citations():
    d = load()
    for p in PAPERS:
        assert [int(x) for x in d[p]["self_citations"]] == EXP[p]["self_citations"], p
