import math
import random
from openpyxl import Workbook

random.seed(11)
wb = Workbook()
ws = wb.active
ws.title = "Prices"
ws.append(["Gold price, US$ per troy ounce (synthetic extract)"])
ws.append(["Source: synthetic IMF-style commodity price data"])
ws.append(["Period", "Gold"])
p = 1750.0 + random.uniform(-100, 100)
y, m = 2022, 1
for i in range(36):
    ws.append([f"{y}M{m:02d}", round(p, 2)])
    p *= math.exp(random.gauss(0.007, 0.035))
    m += 1
    if m > 12:
        m = 1
        y += 1
wb.save("gold_prices.xlsx")
