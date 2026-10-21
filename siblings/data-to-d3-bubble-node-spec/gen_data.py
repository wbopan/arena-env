import csv
import os
import random

random.seed(20240607)
os.makedirs("data", exist_ok=True)

SECTORS = ["Technology", "Healthcare", "Financial Services", "Energy", "Consumer Cyclical"]
WORDS = ["Apex", "Blue", "Cedar", "Delta", "Echo", "Falcon", "Granite", "Harbor", "Iron", "Juniper", "Kestrel", "Lumen", "Maple", "Nova", "Orion", "Pine", "Quartz", "River", "Summit", "Titan", "Union", "Vertex", "Willow", "Zenith"]
SUFFIX = ["Corp", "Inc.", "Holdings", "Group", "Systems", "Labs"]

used = set()


def new_ticker():
    while True:
        t = "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(random.randint(2, 4)))
        if t not in used:
            used.add(t)
            return t


def ok(v):
    for div in (1e12, 1e9, 1e6):
        if v >= div:
            m = v / div
            return not (9.99 <= m < 10 or 99.9 <= m < 100 or 999 <= m < 1000)
    return False


rows = []
for i in range(36):
    sector = SECTORS[i] if i < len(SECTORS) else random.choice(SECTORS)
    while True:
        cap = int(10 ** random.uniform(8.6, 12.45))
        if ok(cap):
            break
    t = new_ticker()
    name = f"{random.choice(WORDS)} {random.choice(WORDS)} {random.choice(SUFFIX)}"
    rows.append([t, name, sector, str(cap), "United States", f"https://www.{t.lower()}.com"])
for i in range(6):
    t = new_ticker()
    rows.append([t, f"{random.choice(WORDS)} {random.choice(SECTORS)} ETF", "ETF", "", "", ""])
random.shuffle(rows)

with open("data/stock-descriptions.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["ticker", "name", "sector", "marketCap", "country", "website"])
    w.writerows(rows)
