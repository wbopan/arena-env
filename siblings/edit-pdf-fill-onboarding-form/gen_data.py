import random

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

random.seed(4127)

FIRSTS = [("Margaret", "Maggie"), ("Robert", "Bobby"), ("Elizabeth", "Liz"), ("William", "Bill"),
          ("Katherine", "Kate"), ("Jonathan", "Jon"), ("Theodore", "Teddy"), ("Alexandra", "Alex")]
LASTS = ["Okafor", "Lindqvist", "Moreau", "Tanaka", "Castillo", "Brennan", "Novak", "Haddad"]
DEPTS = ["Finance", "Legal", "Procurement", "Marketing", "Operations", "Human Resources", "Engineering"]

first, nick = random.choice(FIRSTS)
last = random.choice(LASTS)
middle = random.choice("ABCDEFGHJKLMNPRSTW")
legal = f"{first} {middle}. {last}"
emp = f"E-{random.randint(10000, 99999)}"
cur, prev = random.sample(DEPTS, 2)
start = f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
annual = random.randint(52000, 149000)
while annual % 12 == 0:
    annual += 7

items = [
    ("Legal name", legal),
    ("Preferred name", nick),
    ("Employee number", emp),
    ("Current team", cur),
    ("Previous team", prev),
    ("First day", start),
    ("Base pay", f"${annual:,} per year"),
    ("Office", f"Building {random.choice('ABCDE')}, floor {random.randint(2, 9)}"),
    ("Badge number", str(random.randint(1000, 9999))),
]
random.shuffle(items)
with open("update.txt", "w") as f:
    f.write("Onboarding update from HR (supersedes anything on the form)\n\n")
    for k, v in items:
        f.write(f"- {k}: {v}\n")

c = canvas.Canvas("onboarding_form.pdf", pagesize=letter)
c.setFont("Helvetica-Bold", 16)
c.drawString(72, 720, "Employee Onboarding Form")
c.setFont("Helvetica", 11)
fields = [
    ("full_name", "Full legal name", f"{nick} {last}"),
    ("employee_id", "Employee ID", ""),
    ("department", "Department", prev),
    ("start_date", "Start date (MM/DD/YYYY)", ""),
    ("annual_salary", "Annual base salary (USD)", ""),
    ("monthly_salary", "Monthly base salary (USD)", ""),
]
y = 660
for name, label, val in fields:
    c.drawString(72, y + 6, label)
    c.acroForm.textfield(name=name, tooltip=label, value=val, x=250, y=y, width=260, height=20,
                         fontSize=11, borderStyle="inset", forceBorder=True)
    y -= 40
c.setFont("Helvetica-Oblique", 9)
c.drawString(72, 380, "HR use only. Values must match the latest HR record.")
c.save()
