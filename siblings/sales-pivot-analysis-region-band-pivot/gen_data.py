import random
from openpyxl import Workbook

random.seed(4211)
regions = ["North", "South", "East", "West", "Central"]
reps = ["Avery", "Blake", "Casey", "Drew", "Emery", "Finley"]

wb = Workbook()
ws = wb.active
ws.title = "Orders"
ws.append(["OrderID", "Region", "Rep", "Units", "UnitPrice"])
for i in range(1, 181):
    units = random.choice([random.randint(1, 9), random.randint(10, 49), random.randint(50, 120)])
    price = round(random.uniform(3, 250), 2)
    ws.append([f"SO-{i:04d}", random.choice(regions), random.choice(reps), units, price])
wb.save("sales.xlsx")
