import csv
import json
import os
from collections import OrderedDict

import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "hits.csv")
HEADER = ["request_id", "timestamp", "prompt_tokens", "hit_blocks", "hit_tokens"]


@pytest.fixture(scope="module")
def expected():
    with open(os.path.join(WORK, "config.json")) as f:
        cfg = json.load(f)
    bs = cfg["block_size"]
    cap = cfg["cache_capacity_blocks"]
    with open(os.path.join(WORK, "trace.jsonl")) as f:
        lines = [json.loads(x) for x in f if x.strip()]
    indexed = sorted(enumerate(lines), key=lambda p: (p[1]["timestamp"], p[0]))
    cache = OrderedDict()
    rows = []
    for _, r in indexed:
        k = 0
        while k < len(r["hash_ids"]) and r["hash_ids"][k] in cache:
            k += 1
        for h in r["hash_ids"]:
            if h in cache:
                cache.move_to_end(h)
            else:
                cache[h] = 1
                while len(cache) > cap:
                    cache.popitem(last=False)
        rows.append({"request_id": r["request_id"], "timestamp": r["timestamp"],
                     "prompt_tokens": r["input_length"], "hit_blocks": k,
                     "hit_tokens": min(k * bs, r["input_length"])})
    return rows


@pytest.fixture(scope="module")
def actual():
    assert os.path.exists(OUT), "hits.csv not created"
    with open(OUT, newline="") as f:
        reader = csv.reader(f)
        rows = [[c.strip() for c in row] for row in reader if row]
    return rows


def test_header(actual):
    assert actual[0] == HEADER, f"header {actual[0]}"


def test_order_and_count(actual, expected):
    body = actual[1:]
    assert len(body) == len(expected)
    assert [r[0] for r in body] == [e["request_id"] for e in expected], "rows not in processing order"


def test_prompt_tokens_and_timestamp(actual, expected):
    for r, e in zip(actual[1:], expected):
        assert int(r[1]) == e["timestamp"]
        assert int(r[2]) == e["prompt_tokens"]


def test_hit_blocks(actual, expected):
    bad = [(e["request_id"], r[3], e["hit_blocks"]) for r, e in zip(actual[1:], expected)
           if int(r[3]) != e["hit_blocks"]]
    assert not bad, f"hit_blocks mismatches (id, got, want): {bad[:5]}"


def test_hit_tokens(actual, expected):
    bad = [(e["request_id"], r[4], e["hit_tokens"]) for r, e in zip(actual[1:], expected)
           if int(r[4]) != e["hit_tokens"]]
    assert not bad, f"hit_tokens mismatches (id, got, want): {bad[:5]}"
    assert sum(int(r[4]) for r in actual[1:]) == sum(e["hit_tokens"] for e in expected)
