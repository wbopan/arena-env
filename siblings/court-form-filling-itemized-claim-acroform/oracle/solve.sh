#!/bin/bash
cd /root/work
cat > /tmp/solve.py <<'EOF'
import csv, json, datetime
from pypdf import PdfReader, PdfWriter
case = json.load(open("case.json"))
rows = [r for r in csv.DictReader(open("expenses.csv")) if r["status"] == "unpaid"]
total = round(sum(float(r["amount"]) for r in rows), 2)
ds = sorted(datetime.datetime.strptime(r["date"], "%m/%d/%Y").date() for r in rows)
p = case["plaintiff"]["phone"]
fd = datetime.datetime.strptime(case["filing_date"], "%B %d, %Y").date()
vals = {
    "plaintiff_name": case["plaintiff"]["name"],
    "plaintiff_address": case["plaintiff"]["address"],
    "plaintiff_phone": f"{p[:3]}-{p[3:6]}-{p[6:]}",
    "defendant_name": case["defendant"]["name"],
    "defendant_address": case["defendant"]["address"],
    "claim_amount": f"{total:.2f}",
    "period_start": ds[0].isoformat(),
    "period_end": ds[-1].isoformat(),
    "filing_date": fd.isoformat(),
}
reader = PdfReader("claim_form_blank.pdf")
flds = reader.get_fields()
def on(n):
    st = [str(s) for s in flds[n].get("/_States_", []) if str(s) != "/Off"]
    return st[0] if st else "/Yes"
if total > 2500:
    vals["over_2500"] = on("over_2500")
if case["asked_before_filing"]:
    vals["asked_to_pay"] = on("asked_to_pay")
writer = PdfWriter(clone_from=reader)
writer.update_page_form_field_values(writer.pages[0], vals, auto_regenerate=False)
with open("claim_form_filled.pdf", "wb") as f:
    writer.write(f)
EOF
python3 /tmp/solve.py
