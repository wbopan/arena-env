import json
import math
import os
import re
from collections import Counter

import pytest

W = "/root/work"
OUT = os.path.join(W, "results.json")
TOL = 1e-5


def tok(s):
    return re.findall(r"[a-z0-9]+", s.lower())


def expected():
    docs = []
    with open(os.path.join(W, "corpus.jsonl")) as f:
        for line in f:
            if line.strip():
                docs.append(json.loads(line))
    n = len(docs)
    df = Counter()
    parsed = []
    for d in docs:
        t = tok(d["text"])
        c = Counter(t)
        df.update(c.keys())
        parsed.append((d["doc_id"], c, len(t)))
    idf = {w: math.log((1 + n) / (1 + k)) + 1 for w, k in df.items()}
    vecs = []
    for did, c, L in parsed:
        v = {w: (k / L) * idf[w] for w, k in c.items()}
        nrm = math.sqrt(sum(x * x for x in v.values()))
        vecs.append((did, {w: x / nrm for w, x in v.items()}))
    with open(os.path.join(W, "queries.json")) as f:
        queries = json.load(f)
    res = {}
    for q in queries:
        t = tok(q["text"])
        c = Counter(t)
        L = len(t)
        qv = {w: (k / L) * idf[w] for w, k in c.items() if w in idf}
        nrm = math.sqrt(sum(x * x for x in qv.values()))
        full = {}
        if nrm > 0:
            qv = {w: x / nrm for w, x in qv.items()}
            for did, dv in vecs:
                s = sum(x * dv[w] for w, x in qv.items() if w in dv)
                if s > 0:
                    full[did] = s
        ranked = sorted(full.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        res[q["qid"]] = (ranked, full)
    return res


EXP = expected()


@pytest.fixture(scope="module")
def out():
    assert os.path.isfile(OUT), "results.json missing"
    with open(OUT) as f:
        return json.load(f)


def test_file_exists_and_valid_json():
    assert os.path.isfile(OUT)
    with open(OUT) as f:
        data = json.load(f)
    assert isinstance(data, dict)


def test_all_qids_present(out):
    assert set(out.keys()) == set(EXP.keys())


def test_schema(out):
    for qid, lst in out.items():
        assert isinstance(lst, list)
        assert len(lst) <= 5
        for e in lst:
            assert isinstance(e, dict)
            assert isinstance(e.get("doc_id"), str)
            assert isinstance(e.get("score"), (int, float))


def test_empty_result_queries(out):
    empties = [q for q, (r, _) in EXP.items() if len(r) == 0]
    assert empties, "expected at least one empty query"
    for q in empties:
        assert out[q] == [], f"{q} should have no results"


def test_rankings_and_scores(out):
    for qid, (ranked, full) in EXP.items():
        got = out[qid]
        assert len(got) == len(ranked), f"{qid}: expected {len(ranked)} results, got {len(got)}"
        ids = [e["doc_id"] for e in got]
        assert len(set(ids)) == len(ids), f"{qid}: duplicate doc ids"
        for i, e in enumerate(got):
            exp_score = ranked[i][1]
            assert abs(e["score"] - exp_score) < TOL, f"{qid} pos {i}: score {e['score']} vs {exp_score}"
            assert e["doc_id"] in full, f"{qid} pos {i}: {e['doc_id']} has zero score"
            assert abs(full[e["doc_id"]] - exp_score) < 1e-9 or e["doc_id"] == ranked[i][0], f"{qid} pos {i}: wrong doc {e['doc_id']} (expected {ranked[i][0]})"
