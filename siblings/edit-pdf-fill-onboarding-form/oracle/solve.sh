#!/bin/bash
set -e
cd /root/work
cat > /tmp/fill_form.py <<'EOF'
import re
from decimal import Decimal, ROUND_HALF_UP
from pypdf import PdfWriter

d = {}
for line in open("update.txt"):
    line = line.strip()
    if line.startswith("-") and ":" in line:
        k, v = line.lstrip("- ").split(":", 1)
        d[k.strip()] = v.strip()
y, m, day = d["First day"].split("-")
annual = Decimal(re.sub(r"[^0-9.]", "", d["Base pay"].split()[0])).quantize(Decimal("0.01"))
monthly = (annual / 12).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
vals = {
    "full_name": d["Legal name"],
    "employee_id": d["Employee number"],
    "department": d["Current team"],
    "start_date": f"{m}/{day}/{y}",
    "annual_salary": str(annual),
    "monthly_salary": str(monthly),
}
w = PdfWriter(clone_from="onboarding_form.pdf")
w.update_page_form_field_values(w.pages[0], vals)
with open("onboarding_filled.pdf", "wb") as f:
    w.write(f)
EOF
python3 /tmp/fill_form.py
