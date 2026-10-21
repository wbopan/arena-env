import os
import re
from decimal import Decimal, ROUND_HALF_UP

from pypdf import PdfReader

WORK = "/root/work"
OUT = os.path.join(WORK, "onboarding_filled.pdf")
NAMES = ["full_name", "employee_id", "department", "start_date", "annual_salary", "monthly_salary"]


def parse_update():
    data = {}
    with open(os.path.join(WORK, "update.txt")) as f:
        for line in f:
            line = line.strip()
            if not line.startswith("-") or ":" not in line:
                continue
            k, v = line.lstrip("- ").split(":", 1)
            data[k.strip()] = v.strip()
    return data


def expected():
    d = parse_update()
    y, m, day = d["First day"].split("-")
    annual = Decimal(re.sub(r"[^0-9.]", "", d["Base pay"].split()[0]))
    monthly = (annual / Decimal(12)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {
        "full_name": d["Legal name"],
        "employee_id": d["Employee number"],
        "department": d["Current team"],
        "start_date": f"{m}/{day}/{y}",
        "annual_salary": str(annual.quantize(Decimal("0.01"))),
        "monthly_salary": str(monthly),
        "_nick": d["Preferred name"],
    }


def values():
    fields = PdfReader(OUT).get_fields() or {}
    out = {}
    for n in NAMES:
        if n in fields:
            v = fields[n].get("/V")
            out[n] = "" if v is None else str(v).strip()
    return out


def test_output_exists_one_page():
    assert os.path.isfile(OUT)
    assert len(PdfReader(OUT).pages) == 1


def test_all_fields_present():
    fields = PdfReader(OUT).get_fields() or {}
    for n in NAMES:
        assert n in fields, f"missing form field {n}"


def test_identity_fields():
    e, v = expected(), values()
    assert v.get("full_name") == e["full_name"]
    assert e["_nick"] not in v.get("full_name", "").split()
    assert v.get("employee_id") == e["employee_id"]
    assert v.get("department") == e["department"]


def test_start_date():
    assert values().get("start_date") == expected()["start_date"]


def test_salaries():
    e, v = expected(), values()
    assert v.get("annual_salary") == e["annual_salary"]
    assert v.get("monthly_salary") == e["monthly_salary"]


def test_labels_preserved():
    text = PdfReader(OUT).pages[0].extract_text() or ""
    for s in ["Employee Onboarding Form", "Full legal name", "Start date", "Monthly base salary"]:
        assert s in text
