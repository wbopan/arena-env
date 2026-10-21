import csv
import itertools
import math
import random

random.seed(20220317)

STATES = {
    "Ohio": ["Cleveland", "Columbus", "Cincinnati", "Toledo", "Akron", "Dayton"],
    "Indiana": ["Indianapolis", "Fort Wayne"],
    "Michigan": ["Detroit", "Grand Rapids"],
    "Minnesota": ["Minneapolis", "Duluth"],
}
pairs = [(s, c) for s, cs in STATES.items() for c in cs]
random.shuffle(pairs)
with open("cities.txt", "w") as f:
    for s, c in pairs:
        f.write(f"{s}\t{c}\n")

RULES = ["No smoking", "No parties", "No pets", "No visitors", "No children under 10"]
ROOMS = ["Entire home/apt", "Private room", "Shared room"]
ADJ = ["Cozy", "Sunny", "Modern", "Charming", "Quiet", "Spacious", "Rustic", "Bright", "Elegant", "Lovely"]
NOUN = ["Loft", "Studio", "Cottage", "Suite", "Bungalow", "Apartment", "Retreat", "Townhouse"]


def is_valid(rules, min_n, occ):
    return "No pets" not in rules and occ >= 2 and min_n <= 2


acc_rows = []
for s, c in pairs:
    rows = []
    for i in range(8):
        rules = random.sample(RULES, random.randint(1, 3))
        if c == "Toledo" and "No pets" not in rules:
            rules.append("No pets")
        min_n = random.choice([1, 1, 1, 2, 2, 3, 5])
        occ = random.choice([1, 2, 2, 3, 4, 5])
        price = random.randint(45, 420)
        name = f"{random.choice(ADJ)} {random.choice(NOUN)} in {c} #{i + 1}"
        rows.append([name, price, random.choice(ROOMS), " && ".join(rules), min_n, occ, c])
    if s == "Ohio" and c != "Toledo":
        if not any(is_valid(r[3], r[4], r[5]) for r in rows):
            rows[-1][3] = "No smoking"
            rows[-1][4] = 1
            rows[-1][5] = 2
    acc_rows.extend(rows)
random.shuffle(acc_rows)
with open("accommodations.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["NAME", "price", "room type", "house_rules", "minimum nights", "maximum occupancy", "city"])
    w.writerows(acc_rows)

coords = {"Minneapolis": (0.0, 0.0), "Indianapolis": (880.0, -420.0), "Detroit": (980.0, -80.0)}
for c in STATES["Ohio"]:
    coords[c] = (random.uniform(950, 1250), random.uniform(-450, -150))
ohio = set(STATES["Ohio"])
legs = []
for a in coords:
    for b in coords:
        if a == b:
            continue
        if a in ohio and b in ohio and random.random() < 0.2:
            continue
        base = math.dist(coords[a], coords[b]) * 1.25
        d = int(round(base * random.uniform(0.97, 1.06)))
        cost = int(round(d * random.uniform(0.045, 0.06)))
        mins = int(round(d / 95 * 60))
        legs.append([a, b, f"{mins // 60} hours {mins % 60} mins", d, cost])
random.shuffle(legs)
with open("distance.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["origin", "destination", "duration", "distance_km", "cost"])
    w.writerows(legs)

leg_set = {(r[0], r[1]) for r in legs}
ok_cities = sorted({r[6] for r in acc_rows if r[6] in ohio and is_valid(r[3], r[4], r[5])})
feasible = False
for p in itertools.permutations(ok_cities, 3):
    rt = ["Minneapolis", *p, "Minneapolis"]
    if all((x, y) in leg_set for x, y in zip(rt, rt[1:])):
        feasible = True
        break
assert feasible
