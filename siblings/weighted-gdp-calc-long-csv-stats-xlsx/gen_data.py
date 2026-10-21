import csv
import random

random.seed(777)
countries = [("Bahrain", 38), ("Kuwait", 140), ("Oman", 80), ("Qatar", 180),
             ("Saudi Arabia", 800), ("United Arab Emirates", 420)]
rows = []
for c, b in countries:
    for y in range(2019, 2024):
        g = b * random.uniform(0.85, 1.25)
        x = g * random.uniform(0.35, 0.95)
        m = g * random.uniform(0.3, 0.85)
        for ind, v in (("gdp_current", g), ("exports_gs", x), ("imports_gs", m)):
            if random.random() < 0.4:
                rows.append([c, y, ind, "USD mn", round(v * 1000, 1)])
            else:
                rows.append([c, y, ind, "USD bn", round(v, 4)])
random.shuffle(rows)
with open("trade_long.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["country", "year", "indicator", "unit", "value"])
    w.writerows(rows)
