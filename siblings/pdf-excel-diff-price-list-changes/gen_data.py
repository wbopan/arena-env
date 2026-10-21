import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import Workbook

random.seed(20240331)
ADJ = ["Alpha", "Bravo", "Delta", "Nova", "Prime", "Ultra", "Micro", "Titan"]
NOUN = ["Widget", "Bracket", "Valve", "Sensor", "Cable", "Gasket", "Hinge", "Pump", "Filter"]

codes = random.sample(range(100, 1000), 66)
old_codes = sorted(codes[:60])
new_codes = codes[60:]


def make_item():
    if random.random() < 0.3:
        price = round(random.uniform(1000, 4000), 2)
    else:
        price = round(random.uniform(2, 900), 2)
    return {"name": f"{random.choice(NOUN)} {random.choice(ADJ)}", "price": price, "stock": random.randint(0, 500)}


old = {f"SKU-{c:04d}": make_item() for c in old_codes}

rows = [f"{k} | {v['name']} | {v['price']:,.2f} | {v['stock']}" for k, v in sorted(old.items())]
per_page = 25
pages = [rows[i:i + per_page] for i in range(0, len(rows), per_page)]
c = canvas.Canvas("price_list_backup.pdf", pagesize=letter, invariant=1)
for p, chunk in enumerate(pages):
    y = 740
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Supplier Price List - Backup of 2024-03-31")
    y -= 26
    c.setFont("Helvetica", 9)
    c.drawString(50, y, "SKU | Product | Unit Price (USD) | Stock")
    y -= 18
    for r in chunk:
        c.drawString(50, y, r)
        y -= 14
    c.drawString(50, 40, f"Page {p + 1} of {len(pages)}")
    c.showPage()
c.save()

keys = sorted(old)
removed = set(random.sample(keys, 4))
remaining = [k for k in keys if k not in removed]
changed = random.sample(remaining, 9)
cur = {k: dict(old[k]) for k in remaining}
for k in changed:
    f = random.choice([random.uniform(0.80, 0.97), random.uniform(1.03, 1.25)])
    newp = round(cur[k]["price"] * f, 2)
    if newp == cur[k]["price"]:
        newp += 0.01
    cur[k]["price"] = round(newp, 2)
others = [k for k in remaining if k not in changed]
for k in random.sample(others, 12):
    cur[k]["stock"] = random.randint(0, 500)
for k in random.sample(others, 3):
    cur[k]["name"] = cur[k]["name"] + " v2"
for cc in new_codes:
    cur[f"SKU-{cc:04d}"] = make_item()

wb = Workbook()
ws = wb.active
ws.title = "Prices"
ws.append(["SKU", "Product", "Unit Price", "Stock"])
order = list(cur)
random.shuffle(order)
for k in order:
    v = cur[k]
    ws.append([k, v["name"], v["price"], v["stock"]])
wb.save("price_list_current.xlsx")
