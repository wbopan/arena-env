import random
from openpyxl import Workbook

random.seed(20240611)
firsts = ['Anna', 'Ben', 'Clara', 'David', 'Elif', 'Finn', 'Greta', 'Hugo', 'Ines', 'Jonas', 'Kira', 'Lars', 'Mia', 'Noah', 'Olga', 'Paul']
lasts = ['Schmidt', 'Novak', 'Berg', 'Klein', 'Vogel', 'Roth', 'Lang', 'Wolf', 'Braun', 'Huber']

def r25(x):
    return round(x / 2.5) * 2.5

wb = Workbook()
ws = wb.active
ws.title = 'Results'
ws.append(['Name', 'Sex', 'Equipment', 'Event', 'BodyweightKg', 'Best3SquatKg', 'Best3BenchKg', 'Best3DeadliftKg'])
used = set()
for i in range(45):
    while True:
        name = random.choice(firsts) + ' ' + random.choice(lasts)
        if name not in used:
            used.add(name)
            break
    sex = random.choice(['M', 'M', 'F', 'F', 'Mx'])
    eq = random.choice(['Raw', 'Wraps', 'Single-ply', 'Multi-ply'])
    ev = random.choice(['SBD', 'SBD', 'B'])
    if sex == 'F':
        bw = round(random.uniform(44, 120), 2)
        k = 0.62
    else:
        bw = round(random.uniform(55, 160), 2)
        k = 1.0
    if i == 3:
        bw = 34.2
    eqk = 1.15 if eq in ('Single-ply', 'Multi-ply') else 1.0
    sq = r25(random.uniform(1.4, 2.6) * bw * k * eqk)
    bp = r25(random.uniform(0.9, 1.7) * bw * k * eqk)
    dl = r25(random.uniform(1.7, 3.0) * bw * k)
    if ev == 'SBD':
        if i == 5 or random.random() < 0.07:
            sq = -sq
        if i == 7:
            dl = None
        ws.append([name, sex, eq, ev, bw, sq, bp, dl])
    else:
        if i == 9 or random.random() < 0.05:
            bp = -bp
        ws.append([name, sex, eq, ev, bw, None, bp, None])
wb.save('meet.xlsx')
