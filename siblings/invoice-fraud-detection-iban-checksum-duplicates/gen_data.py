import csv
import random

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

random.seed(4711)

VENDORS = [
    ("V101", "Acme Corporation"),
    ("V102", "Bluewave Logistics Ltd"),
    ("V103", "Northwind Traders Inc"),
    ("V104", "Helix Medical Supplies"),
    ("V105", "Orion Data Systems"),
    ("V106", "Granite Peak Builders Co"),
]
VARIANTS = {
    "V101": ["Acme Corporation", "ACME Corp.", "Acme Corp"],
    "V102": ["Bluewave Logistics Ltd", "Bluewave Logistics Limited", "BlueWave Logistics Ltd."],
    "V103": ["Northwind Traders Inc", "Northwind Traders, Incorporated", "Northwnd Traders Inc"],
    "V104": ["Helix Medical Supplies", "Helix Medcal Supplies", "HELIX MEDICAL SUPPLIES"],
    "V105": ["Orion Data Systems", "Orion Data Sytems", "Orion Data Systems"],
    "V106": ["Granite Peak Builders Co", "Granite Peak Builders Company", "Granite-Peak Builders Co."],
}
UNKNOWN = ["Shadow Freight LLC", "Quickpay Solutions Group"]


def numeric(s):
    return "".join(str(int(c, 36)) for c in s)


def make_iban(valid):
    cc = random.choice(["DE", "NL", "FR", "GB"])
    bban = "".join(random.choice("0123456789") for _ in range(18))
    check = 98 - int(numeric(bban + cc + "00")) % 97
    if not valid:
        pos = random.randrange(len(bban))
        d = bban[pos]
        nd = random.choice([x for x in "0123456789" if x != d])
        bban = bban[:pos] + nd + bban[pos + 1:]
    iban = cc + f"{check:02d}" + bban
    return " ".join(iban[i:i + 4] for i in range(0, len(iban), 4))


ids = [v[0] for v in VENDORS]
records = []
for i in range(14):
    if i in (4, 10):
        vid = None
        name = UNKNOWN[0 if i == 4 else 1]
    else:
        vid = random.choice(ids)
        name = random.choice(VARIANTS[vid])
    amount = round(random.uniform(250, 9800), 2)
    records.append({"vid": vid, "name": name, "amount": amount, "valid": random.random() > 0.3})

known = [i for i, r in enumerate(records) if r["vid"]]
for src in random.sample(known[:9], 3):
    r = records[src]
    records.append({"vid": r["vid"], "name": random.choice(VARIANTS[r["vid"]]),
                    "amount": r["amount"], "valid": random.random() > 0.3})
records.append(dict(records[4]))
other = [v for v in ids if v != records[0]["vid"]][2]
records.append({"vid": other, "name": VARIANTS[other][1], "amount": records[0]["amount"], "valid": True})

c = canvas.Canvas("invoices.pdf", pagesize=letter, pageCompression=1)
for k, r in enumerate(records):
    inv_no = f"INV-{5000 + k * 13 + random.randint(0, 9)}"
    date = f"2024-{random.randint(1, 6):02d}-{random.randint(1, 28):02d}"
    lines = [
        "INVOICE",
        f"Invoice No: {inv_no}",
        f"Date: {date}",
        f"Vendor: {r['name']}",
        f"IBAN: {make_iban(r['valid'])}",
        f"Amount: EUR {r['amount']:,.2f}",
        "Payment terms: Net 30",
    ]
    c.setFont("Helvetica", 12)
    y = 720
    for ln in lines:
        c.drawString(72, y, ln)
        y -= 22
    c.showPage()
c.save()

with open("vendors.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["vendor_id", "vendor_name"])
    for v in VENDORS:
        w.writerow(v)
