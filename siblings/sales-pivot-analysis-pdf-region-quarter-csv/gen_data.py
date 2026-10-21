import random
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import Workbook

random.seed(907)
stores = [("S01", "Harbor Plaza", "Coastal"), ("S02", "Bayfront", "Coastal"),
          ("S03", "Ridge Point", "Inland"), ("S04", "Prairie Mall", "Inland"),
          ("S05", "Downtown Hub", "Metro"), ("S06", "Uptown Square", "Metro"),
          ("S07", "Riverbend", "Valley"), ("S08", "Orchard Lane", "Valley")]
cats = ["Grocery", "Apparel", "Hardware", "Electronics", "Garden"]

wb = Workbook()
ws = wb.active
ws.title = "Stores"
ws.append(["StoreID", "StoreName", "Region"])
for s in stores:
    ws.append(list(s))
wb.save("stores.xlsx")

start = datetime.date(2024, 1, 1)
tx = []
for _ in range(150):
    d = start + datetime.timedelta(days=random.randint(0, 365))
    st = random.choice(stores)[0]
    amt = round(random.uniform(5, 900), 2)
    if random.random() < 0.08:
        amt = -round(random.uniform(5, 120), 2)
    tx.append((d, st, random.choice(cats), amt))
tx.sort(key=lambda t: (t[0], t[1]))

c = canvas.Canvas("transactions.pdf", pagesize=letter)
per_page = 45
pages = (len(tx) + per_page - 1) // per_page
for p in range(pages):
    c.setFont("Courier-Bold", 11)
    c.drawString(50, 760, "Transaction Ledger FY2024")
    c.drawString(50, 742, f"{'Date':<12}{'Store':<7}{'Category':<13}{'Amount':>10}")
    c.setFont("Courier", 10)
    y = 725
    for d, st, cat, amt in tx[p * per_page:(p + 1) * per_page]:
        c.drawString(50, y, f"{d.isoformat():<12}{st:<7}{cat:<13}{amt:>10.2f}")
        y -= 14
    c.drawString(50, 40, f"Page {p + 1} of {pages}")
    c.showPage()
c.save()
