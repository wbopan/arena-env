import random

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

random.seed(9031)

FIRST = ["Ana", "Bruno", "Chen", "Dalia", "Emeka", "Farah", "Goran", "Hana", "Ivan", "Jalen",
         "Keiko", "Luis", "Mira", "Nils", "Omar", "Priya", "Quinn", "Rosa", "Sven", "Tara"]
LAST = ["Abara", "Berg", "Costa", "Duarte", "Eklund", "Fischer", "Gupta", "Holm", "Ito", "Jensen",
        "Kowalski", "Lopez", "Mendes", "Nakamura", "Ortiz", "Petrov", "Reyes", "Silva", "Varga", "Weber"]

c = canvas.Canvas("register.pdf", pagesize=letter, pageCompression=0)
used = set()
for p in range(2):
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, 740, f"Quarterly Account Register - Page {p + 1} of 2")
    c.setFont("Helvetica", 10)
    c.drawString(72, 716, "Customer | Account | Branch | Balance")
    y = 694
    for i in range(random.randint(12, 16)):
        while True:
            acct = str(random.randint(1000000000, 9999999999))
            if acct not in used:
                used.add(acct)
                break
        name = f"{random.choice(FIRST)} {random.choice(LAST)}"
        br = random.randint(1, 9999)
        bal = random.randint(1000, 250000000) / 100
        c.drawString(72, y, f"{name} | Acct {acct} | Branch BR-{br:04d} | Balance ${bal:,.2f}")
        y -= 20
    c.drawString(72, 60, f"Batch {random.randint(10000000, 99999999)} | Records Office ext. {random.randint(1000, 9999)}")
    c.showPage()
c.save()
