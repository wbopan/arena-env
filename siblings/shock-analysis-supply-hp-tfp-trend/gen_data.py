import random, math
from openpyxl import Workbook

random.seed(11)
alpha = round(random.uniform(0.30, 0.40), 3)
k = random.uniform(70, 110)
lnz = random.uniform(1.3, 1.7)
rows = []
for i, yr in enumerate(range(2000, 2024)):
    k *= 1 + random.uniform(0.02, 0.06)
    lnz += random.uniform(-0.015, 0.035) + 0.02 * math.sin(i / 2.0)
    y = math.exp(lnz) * k ** alpha
    d = random.uniform(0.04, 0.075)
    rows.append([yr, round(k, 3), round(y, 3), round(d * k, 3)])
random.shuffle(rows)
wb = Workbook()
ws = wb.active
ws.title = 'Macro'
ws.append(['year', 'K', 'Y', 'CFC'])
for r in rows:
    ws.append(r)
p = wb.create_sheet('Params')
p.append(['parameter', 'value'])
p.append(['alpha', alpha])
p.append(['hp_lambda', 100])
wb.save('macro_data.xlsx')
