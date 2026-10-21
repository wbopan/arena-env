import csv
import os
import re
from difflib import SequenceMatcher

import pytest
from pypdf import PdfReader

WORK = "/root/work"
OUT = os.path.join(WORK, "invoice_audit.csv")
HEADER = ["page", "invoice_no", "vendor_id", "amount", "iban_valid", "duplicate_of"]
TOKMAP = {"limited": "ltd", "corporation": "corp", "incorporated": "inc", "company": "co"}


def norm(s):
    s = re.sub(r"[^a-z0-9\s]", "", s.lower())
    return " ".join(TOKMAP.get(t, t) for t in s.split())


def iban_ok(s):
    s = re.sub(r"\s", "", s).upper()
    if len(s) < 5 or not s.isalnum():
        return False
    r = s[4:] + s[:4]
    return int("".join(str(int(ch, 36)) for ch in r)) % 97 == 1


def compute_expected():
    with open(os.path.join(WORK, "vendors.csv"), newline="") as f:
        vendors = [(r["vendor_id"], norm(r["vendor_name"])) for r in csv.DictReader(f)]
    rows = []
    first_seen = {}
    for i, p in enumerate(PdfReader(os.path.join(WORK, "invoices.pdf")).pages, 1):
        t = p.extract_text()
        inv = re.search(r"Invoice No:\s*(\S+)", t).group(1)
        name = re.search(r"Vendor:[ \t]*(.+)", t).group(1).strip()
        iban = re.search(r"IBAN:[ \t]*([A-Za-z0-9 ]+)", t).group(1).strip()
        amt = float(re.search(r"Amount:\s*[A-Z]{3}\s*([\d,]+\.\d{2})", t).group(1).replace(",", ""))
        n = norm(name)
        vid = "UNKNOWN"
        exact = [v for v, vn in vendors if vn == n]
        if exact:
            vid = exact[0]
        else:
            best, score = None, -1.0
            for v, vn in vendors:
                r = SequenceMatcher(None, n, vn).ratio()
                if r > score:
                    best, score = v, r
            if score >= 0.85:
                vid = best
        dup = None
        if vid != "UNKNOWN":
            key = (vid, round(amt * 100))
            if key in first_seen:
                dup = first_seen[key]
            else:
                first_seen[key] = i
        rows.append({"page": i, "invoice_no": inv, "vendor_id": vid, "amount": amt,
                     "iban_valid": iban_ok(iban), "duplicate_of": dup})
    return rows


@pytest.fixture(scope="module")
def expected():
    return compute_expected()


@pytest.fixture(scope="module")
def actual():
    with open(OUT, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [r for r in reader if any(x.strip() for x in r)]
    return header, rows


def test_file_exists():
    assert os.path.exists(OUT), "invoice_audit.csv not found"


def test_header_and_pages(expected, actual):
    header, rows = actual
    assert [h.strip() for h in header] == HEADER
    assert [int(r[0]) for r in rows] == [e["page"] for e in expected]
    for r in rows:
        assert re.fullmatch(r"-?\d+\.\d{2}", r[3].strip()), f"bad amount format {r[3]}"


def test_invoice_no_and_amount(expected, actual):
    _, rows = actual
    for e, r in zip(expected, rows):
        assert r[1].strip() == e["invoice_no"], f"page {e['page']}"
        assert abs(float(r[3]) - e["amount"]) < 0.005, f"page {e['page']}"


def test_vendor_ids(expected, actual):
    _, rows = actual
    for e, r in zip(expected, rows):
        assert r[2].strip() == e["vendor_id"], f"page {e['page']}: expected {e['vendor_id']}, got {r[2]}"


def test_iban_valid(expected, actual):
    _, rows = actual
    for e, r in zip(expected, rows):
        assert r[4].strip().lower() == ("true" if e["iban_valid"] else "false"), f"page {e['page']}"


def test_duplicates(expected, actual):
    _, rows = actual
    for e, r in zip(expected, rows):
        exp = "" if e["duplicate_of"] is None else str(e["duplicate_of"])
        assert r[5].strip() == exp, f"page {e['page']}: expected '{exp}', got '{r[5]}'"
