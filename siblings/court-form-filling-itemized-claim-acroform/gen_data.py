import random, csv, json, datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

random.seed(4127)
first = ["Maria", "Kevin", "Aisha", "Tomas", "Lena", "Raj", "Grace", "Omar", "Sofia", "Daniel"]
last = ["Alvarez", "Nguyen", "Okafor", "Schmidt", "Patel", "Kim", "Rossi", "Haddad", "Larsen", "Brooks"]
streets = ["Maple St", "Oak Ave", "Elm Dr", "Cedar Ln", "Birch Rd", "Pine Ct"]
cities = [("Fresno", "93721"), ("Oakland", "94607"), ("San Jose", "95112"), ("Pasadena", "91101")]

def person():
    c = random.choice(cities)
    return (random.choice(first) + " " + random.choice(last),
            f"{random.randint(100, 9999)} {random.choice(streets)}, {c[0]}, CA {c[1]}")

pn, pa = person()
dn, da = person()
while dn == pn:
    dn, da = person()
phone = str(random.randint(2, 9)) + "".join(str(random.randint(0, 9)) for _ in range(9))
fd = datetime.date(2026, 1, 5) + datetime.timedelta(days=random.randint(0, 120))
case = {
    "plaintiff": {"name": pn, "address": pa, "phone": phone},
    "defendant": {"name": dn, "address": da},
    "filing_date": f"{fd.strftime('%B')} {fd.day}, {fd.year}",
    "asked_before_filing": random.random() < 0.5,
}
with open("case.json", "w") as f:
    json.dump(case, f, indent=2)

descs = ["Roof leak repair", "Water damage cleanup", "Replacement carpet", "Plumber visit",
         "Unreturned deposit share", "Utility bill share", "Damaged furniture", "Locksmith",
         "Mold remediation", "Appliance repair", "Hotel stay", "Moving truck"]
rows = []
base = datetime.date(2025, 5, 1)
for i, d in enumerate(descs):
    dt = base + datetime.timedelta(days=random.randint(0, 200))
    amt = round(random.uniform(40, 650), 2)
    st = "unpaid" if random.random() < 0.6 else "paid"
    rows.append([dt.strftime("%m/%d/%Y"), d, f"{amt:.2f}", st])
rows[0][3] = "unpaid"
rows[1][3] = "unpaid"
random.shuffle(rows)
with open("expenses.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["date", "description", "amount", "status"])
    w.writerows(rows)

c = canvas.Canvas("claim_form_blank.pdf", pagesize=letter)
c.setFont("Helvetica-Bold", 14)
c.drawString(60, 750, "PLAINTIFF'S CLAIM - SMALL CLAIMS COURT")
c.setFont("Helvetica", 10)
fields = [("case_number", "Case number (court use only)"), ("plaintiff_name", "Plaintiff name"),
          ("plaintiff_phone", "Plaintiff phone"), ("plaintiff_address", "Plaintiff address"),
          ("defendant_name", "Defendant name"), ("defendant_address", "Defendant address"),
          ("claim_amount", "Amount claimed (USD)"), ("period_start", "Period start"),
          ("period_end", "Period end"), ("filing_date", "Date filed")]
y = 710
for n, lab in fields:
    c.drawString(60, y, lab)
    c.acroForm.textfield(name=n, tooltip=lab, x=230, y=y - 5, width=320, height=18,
                         borderStyle="inset", forceBorder=True, fontSize=10)
    y -= 40
for n, lab in [("over_2500", "Claim exceeds $2,500"), ("asked_to_pay", "I asked the defendant to pay before filing")]:
    c.acroForm.checkbox(name=n, tooltip=lab, x=60, y=y - 3, size=12, checked=False, buttonStyle="check")
    c.drawString(80, y, lab)
    y -= 30
c.showPage()
c.save()
