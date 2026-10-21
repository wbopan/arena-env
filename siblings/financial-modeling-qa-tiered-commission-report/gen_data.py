import random
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

random.seed(4242)
clients = ["ACME", "BRAVO", "CEDAR", "DELTA", "EMBER", "FALCON"]
trades = []
for i in range(77):
    bucket = random.random()
    if bucket < 0.35:
        qty = random.randint(5, 60)
    elif bucket < 0.75:
        qty = random.randint(100, 900)
    else:
        qty = random.randint(1000, 3000)
    price = round(random.uniform(2, 300), 2)
    trades.append([random.choice(clients), random.choice(["BUY", "SELL"]), qty, price])
# exact tier-boundary trades
trades.append(["BRAVO", "SELL", 100, 100.0])
trades.append(["DELTA", "BUY", 500, 100.0])
trades.append(["ACME", "SELL", 1000, 200.0])
random.shuffle(trades)

wb = Workbook()
ws = wb.active
ws.title = "Trades"
ws.append(["trade_id", "client", "side", "quantity", "price"])
for i, t in enumerate(trades, 1):
    ws.append([f"T{i:04d}"] + t)
wb.save("data.xlsx")

lines = [
    "Brokerage Commission Schedule (effective for all accounts)",
    "",
    "Notional = quantity x price, in USD.",
    "The rate of the tier containing the trade's notional applies to the ENTIRE notional.",
    "Tier lower bounds are inclusive.",
    "Tier A: 0 <= notional < 10,000          rate 0.30%",
    "Tier B: 10,000 <= notional < 50,000     rate 0.20%",
    "Tier C: 50,000 <= notional < 200,000    rate 0.12%",
    "Tier D: notional >= 200,000             rate 0.08%",
    "Minimum commission per trade: 7.50 USD (applies to the commission only).",
    "SELL trades additionally pay a regulatory fee of 0.0025% of notional (no minimum).",
    "Total charge per trade = commission + regulatory fee.",
]
c = canvas.Canvas("background.pdf", pagesize=letter)
y = 740
for line in lines:
    c.drawString(50, y, line)
    y -= 18
c.save()
