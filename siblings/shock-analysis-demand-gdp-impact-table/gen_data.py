import json
import math
import random
from openpyxl import Workbook

random.seed(2026)
wb = Workbook()
ws = wb.active
ws.title = "WEO_Data"
ws.append(["Year", "Nominal GDP (bn GEL)", "Real GDP growth (%)", "GDP deflator (2019=100)"])
real = 48.0 + random.uniform(-3, 3)
defl = 100.0
for y in range(2019, 2034):
    if y <= 2025:
        g = round(random.uniform(2.5, 8.5), 1)
        if y > 2019:
            real *= 1 + g / 100
            defl *= 1 + random.uniform(0.03, 0.10)
        ws.append([y, round(real * defl / 100, 3), g, round(defl, 2)])
    else:
        g = round(random.uniform(3.5, 5.5), 1)
        ws.append([y, None, g, None])
wb.save("weo.xlsx")

width = random.uniform(1.5, 2.5)
weights = [round(10 * math.exp(-((i - 3.5) / width) ** 2 / 2) + random.uniform(0, 0.5), 2) for i in range(8)]
params = {
    "total_investment_usd_bn": round(random.uniform(4, 8), 2),
    "fx_gel_per_usd": 2.746,
    "demand_multiplier": random.choice([0.7, 0.8, 0.9, 1.0]),
    "import_content_share": round(random.uniform(0.3, 0.6), 3),
    "start_year": 2026,
    "allocation_weights": weights,
}
with open("params.json", "w") as f:
    json.dump(params, f, indent=2)
