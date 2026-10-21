import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import Workbook

random.seed(777)
FIRST = ["Ana", "Ben", "Chloe", "David", "Elena", "Farid", "Grace", "Hugo", "Iris", "Jonas", "Keiko", "Liam", "Maya", "Nils", "Olga", "Pedro"]
LAST = ["Smith", "Garcia", "Chen", "Novak", "Okafor", "Muller", "Rossi", "Tanaka", "Silva", "Kowalski", "Haddad", "Berg"]
DEPTS = ["Engineering", "Finance", "Marketing", "Operations", "Sales", "Support"]

ids = random.sample(range(1, 400), 64)
old_ids = sorted(ids[:56])
hire_ids = ids[56:]


def person(dept=None):
    d = dept or random.choice(DEPTS)
    return {
        "name": f"{random.choice(FIRST)} {random.choice(LAST)}",
        "dept": d,
        "salary": random.randint(90, 360) * 500,
        "start": f"{random.randint(2010, 2023)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
    }


old = {f"EMP{i:05d}": person() for i in old_ids}

rows = [f"{k} | {v['name']} | {v['dept']} | ${v['salary']:,} | {v['start']}" for k, v in sorted(old.items())]
per_page = 22
pages = [rows[i:i + per_page] for i in range(0, len(rows), per_page)]
c = canvas.Canvas("roster_backup.pdf", pagesize=letter, invariant=1)
for p, chunk in enumerate(pages):
    y = 740
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Employee Roster - Archived 2023-12-31")
    y -= 26
    c.setFont("Helvetica", 9)
    c.drawString(50, y, "ID | Name | Department | Salary | Start Date")
    y -= 18
    for r in chunk:
        c.drawString(50, y, r)
        y -= 14
    c.drawString(50, 40, f"Confidential - page {p + 1} of {len(pages)}")
    c.showPage()
c.save()

keys = sorted(old)
removed = set(random.sample(keys, 5))
remaining = [k for k in keys if k not in removed]
cur = {k: dict(old[k]) for k in remaining}
for k in random.sample(remaining, 6):
    cur[k]["dept"] = random.choice([d for d in DEPTS if d != cur[k]["dept"]])
for k in random.sample(remaining, 10):
    cur[k]["salary"] += random.randint(2, 12) * 500
for n, i in enumerate(hire_ids):
    cur[f"EMP{i:05d}"] = person("Legal" if n < 3 else None)

wb = Workbook()
ws = wb.active
ws.title = "Employees"
ws.append(["Employee ID", "Name", "Department", "Annual Salary"])
order = list(cur)
random.shuffle(order)
for k in order:
    v = cur[k]
    ws.append([k, v["name"], v["dept"], v["salary"]])
wb.save("roster_current.xlsx")
