import csv, json, datetime
from decimal import Decimal
from pathlib import Path
import pytest
from pypdf import PdfReader

W = Path("/root/work")
OUT = W / "claim_form_filled.pdf"


def expected():
    case = json.loads((W / "case.json").read_text())
    rows = list(csv.DictReader(open(W / "expenses.csv")))
    unpaid = [r for r in rows if r["status"].strip() == "unpaid"]
    total = sum(Decimal(r["amount"]) for r in unpaid)
    dates = [datetime.datetime.strptime(r["date"], "%m/%d/%Y").date() for r in unpaid]
    p = case["plaintiff"]["phone"]
    fd = datetime.datetime.strptime(case["filing_date"], "%B %d, %Y").date()
    return {
        "text": {
            "plaintiff_name": case["plaintiff"]["name"],
            "plaintiff_address": case["plaintiff"]["address"],
            "plaintiff_phone": f"{p[:3]}-{p[3:6]}-{p[6:]}",
            "defendant_name": case["defendant"]["name"],
            "defendant_address": case["defendant"]["address"],
            "claim_amount": f"{total:.2f}",
            "period_start": min(dates).isoformat(),
            "period_end": max(dates).isoformat(),
            "filing_date": fd.isoformat(),
        },
        "over_2500": total > Decimal("2500"),
        "asked_to_pay": bool(case["asked_before_filing"]),
    }


def fields():
    return PdfReader(str(OUT)).get_fields() or {}


def val(f, n):
    v = f.get(n, {}).get("/V")
    return "" if v is None else str(v).strip()


def checked(f, n):
    v = val(f, n).lstrip("/")
    return v not in ("", "Off")


def test_output_exists_with_fields():
    assert OUT.exists()
    f = fields()
    for n in ["plaintiff_name", "claim_amount", "over_2500", "case_number"]:
        assert n in f


def test_party_fields():
    e, f = expected()["text"], fields()
    for n in ["plaintiff_name", "plaintiff_address", "plaintiff_phone", "defendant_name", "defendant_address"]:
        assert val(f, n) == e[n], n


def test_claim_amount():
    e, f = expected()["text"], fields()
    assert val(f, "claim_amount") == e["claim_amount"]


def test_dates():
    e, f = expected()["text"], fields()
    for n in ["period_start", "period_end", "filing_date"]:
        assert val(f, n) == e[n], n


def test_checkboxes():
    e, f = expected(), fields()
    assert checked(f, "over_2500") == e["over_2500"]
    assert checked(f, "asked_to_pay") == e["asked_to_pay"]


def test_court_field_empty():
    assert val(fields(), "case_number") == ""
