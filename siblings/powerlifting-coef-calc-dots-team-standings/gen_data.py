import csv
import random

random.seed(4242)
teams = ['Berlin Barbell', 'Koeln Iron', 'Hamburg Strength', 'Munich Power', 'Leipzig Lifters', 'Dresden Deadlift']
firsts = ['Anna', 'Ben', 'Clara', 'David', 'Elif', 'Finn', 'Greta', 'Hugo', 'Ines', 'Jonas', 'Kira', 'Lars', 'Mia', 'Noah', 'Olga', 'Paul', 'Rosa', 'Sven']
lasts = ['Schmidt', 'Novak', 'Berg', 'Klein', 'Vogel', 'Roth', 'Lang', 'Wolf', 'Braun', 'Huber', 'Kraus', 'Fuchs']

def r25(x):
    return round(x / 2.5) * 2.5

used = set()
rows = []
forced = [('F', 156.3), ('M', 214.0), ('M', 37.5), ('Mx', 92.4)]
for ti, team in enumerate(teams):
    n = random.randint(4, 7)
    bomb_idx = random.randrange(n) if random.random() < 0.5 else -1
    for j in range(n):
        while True:
            name = random.choice(firsts) + ' ' + random.choice(lasts)
            if name not in used:
                used.add(name)
                break
        sex = random.choice(['M', 'M', 'F', 'F', 'Mx'])
        bw = round(random.uniform(46, 125) if sex == 'F' else random.uniform(58, 150), 1)
        if j == 0 and ti < len(forced):
            sex, bw = forced[ti]
        k = 0.62 if sex == 'F' else 1.0
        base = min(max(bw, 45), 140)
        sq = r25(random.uniform(1.4, 2.6) * base * k)
        bp = r25(random.uniform(0.9, 1.6) * base * k)
        dl = r25(random.uniform(1.7, 3.0) * base * k)
        vals = [str(sq), str(bp), str(dl)]
        if j == bomb_idx:
            if random.random() < 0.5:
                vals[2] = ''
            else:
                vals[0] = str(-sq)
        rows.append([name, team, sex, str(bw)] + vals)
random.shuffle(rows)
with open('lifters.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['Name', 'Team', 'Sex', 'BodyweightKg', 'Best3SquatKg', 'Best3BenchKg', 'Best3DeadliftKg'])
    w.writerows(rows)
