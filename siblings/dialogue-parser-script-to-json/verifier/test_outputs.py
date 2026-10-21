import json
import os
import pytest

OUT = "/root/work/dialogue.json"
SRC = "/root/work/script.txt"


def expected():
    nodes, edges = [], []
    cur = None
    with open(SRC, encoding="utf-8") as f:
        for raw in f:
            s = raw.strip()
            if s == "" or s.startswith("#"):
                continue
            if s.startswith("[") and s.endswith("]") and not s[0].isdigit():
                cur = {"id": s[1:-1].strip(), "text": "", "speaker": "", "type": "line"}
                nodes.append(cur)
                continue
            idx = s.rfind("->")
            body = s[:idx].strip()
            to = s[idx + 2:].strip()
            head, sep, rest = body.partition(".")
            if sep and head.isdigit():
                cur["type"] = "choice"
                edges.append({"from": cur["id"], "to": to, "text": rest.strip()})
            else:
                sp, _, tx = body.partition(":")
                cur["speaker"] = sp.strip()
                cur["text"] = tx.strip()
                edges.append({"from": cur["id"], "to": to, "text": ""})
    return {"start": nodes[0]["id"], "nodes": nodes, "edges": edges}


@pytest.fixture(scope="module")
def data():
    assert os.path.exists(OUT), "dialogue.json missing"
    with open(OUT) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def exp():
    return expected()


def test_schema(data):
    assert set(["start", "nodes", "edges"]) <= set(data.keys())
    for n in data["nodes"]:
        assert set(n.keys()) >= {"id", "text", "speaker", "type"}
        assert n["type"] in ("line", "choice")
    for e in data["edges"]:
        assert set(e.keys()) >= {"from", "to", "text"}


def test_start(data, exp):
    assert data["start"] == exp["start"]


def test_nodes(data, exp):
    got = [{k: n[k] for k in ("id", "text", "speaker", "type")} for n in data["nodes"]]
    assert len(got) == len(exp["nodes"]), "node count mismatch"
    for g, e in zip(got, exp["nodes"]):
        assert g == e, f"node mismatch: {g} != {e}"


def test_edges(data, exp):
    got = [{k: x[k] for k in ("from", "to", "text")} for x in data["edges"]]
    assert len(got) == len(exp["edges"]), "edge count mismatch"
    for g, e in zip(got, exp["edges"]):
        assert g == e, f"edge mismatch: {g} != {e}"
