import glob
import json
import os

WORK = "/root/work"
OUT = os.path.join(WORK, "answer.json")
TARGET = "CoachForce"


def expected():
    docs, meets = [], []
    for path in sorted(glob.glob(os.path.join(WORK, "DATA", "products", "*.json"))):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        docs.extend(data.get("documents", []))
        meets.extend(data.get("meetings", []))
    cands = [d for d in docs if d["type"] == "Market Research Report" and TARGET in d["title"]]
    sel = max(cands, key=lambda d: d["date"])
    authors = set(sel["authors"])
    rev = set(sel.get("reviewers", []))
    for m in meets:
        if m["doc_id"] == sel["id"]:
            for t in m["transcript"]:
                if t["kind"] == "feedback":
                    rev.add(t["speaker"])
    rev -= authors
    return sel["id"], sorted(authors), sorted(rev)


def load():
    with open(OUT, encoding="utf-8") as f:
        return json.load(f)


def test_output_exists():
    assert os.path.exists(OUT), "answer.json missing"
    assert isinstance(load(), dict)


def test_schema():
    a = load()
    for k in ("report_doc_id", "author_ids", "reviewer_ids"):
        assert k in a, f"missing key {k}"
    assert isinstance(a["report_doc_id"], str)
    for k in ("author_ids", "reviewer_ids"):
        assert isinstance(a[k], list)
        assert all(isinstance(x, str) for x in a[k])


def test_report_doc_id():
    doc_id, _, _ = expected()
    assert load()["report_doc_id"] == doc_id


def test_authors():
    _, authors, _ = expected()
    assert load()["author_ids"] == authors


def test_reviewers():
    _, _, rev = expected()
    assert load()["reviewer_ids"] == rev
