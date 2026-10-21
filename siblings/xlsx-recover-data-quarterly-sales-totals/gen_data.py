import random
from openpyxl import Workbook

random.seed(4217)
regions = ["North", "South", "East", "West", "Central", "Pacific", "Mountain", "Atlantic"]
R = len(regions)
grid = [[random.randint(120, 980) * 10 + random.randint(0, 9) for _ in range(4)] for _ in regions]
for row in grid:
    row.append(sum(row))
grid.append([sum(grid[i][j] for i in range(R)) for j in range(5)])

CS = []
for i in range(R + 1):
    CS.append(([(i, j) for j in range(4)], (i, 4)))
for j in range(5):
    CS.append(([(i, j) for i in range(R)], (R, j)))


def peel(missing):
    missing = set(missing)
    rounds = 0
    while missing:
        solv = set()
        for parts, tot in CS:
            m = [c for c in parts + [tot] if c in missing]
            if len(m) == 1:
                solv.add(m[0])
        if not solv:
            return None
        missing -= solv
        rounds += 1
    return rounds


cells = [(i, j) for i in range(R + 1) for j in range(5)]
while True:
    miss = random.sample(cells, 9)
    ntot = sum(1 for i, j in miss if i == R or j == 4)
    r = peel(miss)
    if r is not None and r >= 2 and ntot >= 2:
        break
miss = set(miss)

wb = Workbook()
ws = wb.active
ws.title = "Quarterly Sales"
ws.append(["Region", "Q1", "Q2", "Q3", "Q4", "Total"])
for i in range(R + 1):
    label = regions[i] if i < R else "Total"
    ws.append([label] + [("???" if (i, j) in miss else grid[i][j]) for j in range(5)])
wb.save("sales_incomplete.xlsx")
