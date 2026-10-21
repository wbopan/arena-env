import json
import os
import re

import pytest

W = "/root/work"
OUT = os.path.join(W, "schedule.json")


def compute():
    docs = []
    with open(os.path.join(W, "corpus.jsonl")) as f:
        for line in f:
            if line.strip():
                docs.append(json.loads(line))
    with open(os.path.join(W, "config.json")) as f:
        k = json.load(f)["num_workers"]
    cost, terms = {}, {}
    for d in docs:
        t = re.findall(r"[a-z0-9]+", d["text"].lower())
        cost[d["doc_id"]] = len(t)
        terms[d["doc_id"]] = set(t)
    order = sorted(cost, key=lambda i: (-cost[i], i))
    loads = [0] * k
    assign = [[] for _ in range(k)]
    for i in order:
        w = min(range(k), key=lambda j: (loads[j], j))
        assign[w].append(i)
        loads[w] += cost[i]
    nterms = []
    for a in assign:
        s = set()
        for i in a:
            s |= terms[i]
        nterms.append(len(s))
    mk = max(loads)
    imb = mk / (sum(loads) / k)
    return k, cost, assign, loads, nterms, mk, imb


K, COST, ASSIGN, LOADS, NTERMS, MK, IMB = compute()


@pytest.fixture(scope="module")
def out():
    assert os.path.isfile(OUT), "schedule.json missing"
    with open(OUT) as f:
        return json.load(f)


def test_file_exists_and_schema(out):
    assert isinstance(out, dict)
    for key in ("workers", "makespan", "imbalance"):
        assert key in out
    assert isinstance(out["workers"], list) and len(out["workers"]) == K
    for i, w in enumerate(out["workers"]):
        assert w["worker"] == i
        assert isinstance(w["doc_ids"], list)
        assert isinstance(w["load"], int)
        assert isinstance(w["num_terms"], int)


def test_partition_covers_all_docs(out):
    ids = [d for w in out["workers"] for d in w["doc_ids"]]
    assert sorted(ids) == sorted(COST.keys())


def test_exact_lpt_assignment(out):
    for i, w in enumerate(out["workers"]):
        assert w["doc_ids"] == ASSIGN[i], f"worker {i} assignment mismatch"


def test_loads_and_terms(out):
    for i, w in enumerate(out["workers"]):
        assert w["load"] == LOADS[i], f"worker {i} load {w['load']} vs {LOADS[i]}"
        assert w["num_terms"] == NTERMS[i], f"worker {i} num_terms {w['num_terms']} vs {NTERMS[i]}"


def test_makespan_and_imbalance(out):
    assert out["makespan"] == MK
    assert abs(out["imbalance"] - IMB) < 1e-4
