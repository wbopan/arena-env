import csv
import json
import os
import re

WORK = "/root/work"
OUT = os.path.join(WORK, "doc_reviews.csv")
COLS = ["product", "doc_id", "sharer_id", "n_replies", "reviewer_ids"]
LINK = re.compile(r"/archives/docs/(doc_[0-9a-f]+)")


def expected():
    with open(os.path.join(WORK, "DATA", "slack.json"), encoding="utf-8") as f:
        msgs = json.load(f)
    emp = {}
    with open(os.path.join(WORK, "DATA", "employees.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            emp[(r["team"], r["name"])] = r["employee_id"]
    replies = {}
    for m in msgs:
        if m["parent_id"]:
            replies.setdefault(m["parent_id"], []).append(m)
    rows = {}
    for m in msgs:
        if m["parent_id"] or not m["channel"].startswith("planning-"):
            continue
        mt = LINK.search(m["text"])
        if not mt:
            continue
        prod = m["channel"][len("planning-"):]
        sharer = emp[(prod, m["user_name"])]
        reps = replies.get(m["id"], [])
        rev = set()
        for r in reps:
            if len(r["text"].split()) >= 6:
                rid = emp[(prod, r["user_name"])]
                if rid != sharer:
                    rev.add(rid)
        rows[mt.group(1)] = {"product": prod, "doc_id": mt.group(1), "sharer_id": sharer,
                             "n_replies": len(reps), "reviewer_ids": ";".join(sorted(rev))}
    return rows


def load():
    with open(OUT, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames
        rows = list(reader)
    return header, rows


def test_exists_and_header():
    assert os.path.exists(OUT), "doc_reviews.csv missing"
    header, _ = load()
    assert [h.strip() for h in header] == COLS


def test_rows_and_order():
    exp = expected()
    _, rows = load()
    ids = [r["doc_id"].strip() for r in rows]
    assert sorted(ids) == sorted(exp.keys())
    assert ids == sorted(ids), "rows not sorted by doc_id"


def test_product_and_sharer():
    exp = expected()
    _, rows = load()
    for r in rows:
        e = exp[r["doc_id"].strip()]
        assert r["product"].strip() == e["product"]
        assert r["sharer_id"].strip() == e["sharer_id"], r["doc_id"]


def test_n_replies():
    exp = expected()
    _, rows = load()
    for r in rows:
        assert int(float(r["n_replies"])) == exp[r["doc_id"].strip()]["n_replies"], r["doc_id"]


def test_reviewer_ids():
    exp = expected()
    _, rows = load()
    for r in rows:
        got = (r.get("reviewer_ids") or "").strip()
        assert got == exp[r["doc_id"].strip()]["reviewer_ids"], r["doc_id"]
