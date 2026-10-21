import csv
import datetime
import math
import os
import random

random.seed(4242)
os.makedirs("data/indiv-stock", exist_ok=True)

tickers = ["NOVA", "QRTZ", "HRBR", "PINE", "VTX"]
days = []
d = datetime.date(2023, 3, 1)
while len(days) < 45:
    if d.weekday() < 5:
        days.append(d)
    d += datetime.timedelta(days=1)

for t in tickers:
    s = random.randint(0, 5)
    e = len(days) - random.randint(0, 5)
    sel = [x for x in days[s:e] if random.random() > 0.12]
    price = random.uniform(40, 300)
    rows = []
    for dd in sel:
        price *= math.exp(random.gauss(0, 0.025))
        close = round(price, 2)
        op = round(close * random.uniform(0.98, 1.02), 2)
        hi = round(max(op, close) * random.uniform(1.0, 1.015), 2)
        lo = round(min(op, close) * random.uniform(0.985, 1.0), 2)
        vol = random.randint(100000, 5000000)
        rows.append([dd.isoformat(), f"{op:.2f}", f"{hi:.2f}", f"{lo:.2f}", f"{close:.2f}", vol])
    random.shuffle(rows)
    with open(f"data/indiv-stock/{t}.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
        w.writerows(rows)
