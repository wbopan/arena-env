import csv
import os
import random

random.seed(7713)
TAB = chr(9)

PRE = ["ALPINE", "BOREAL", "CASCADE", "DELTA", "EMBER", "FALCON"]
SUF = ["SYSTEMS INC", "HOLDINGS CORP", "ENERGY CO", "FOODS INC", "BANCORP"]
ALNUM = "0123456789ABCDEFGHJKLMNPRSTUVWXYZ"
used = {"69608A108"}


def mk_cusip():
    while True:
        c = (random.choice("000123456789")
             + "".join(random.choice(ALNUM) for _ in range(5))
             + "".join(random.choice("0123456789") for _ in range(3)))
        if c not in used:
            used.add(c)
            return c


STOCKS = [(p + " " + s, mk_cusip()) for p in PRE for s in SUF]
NAME = {c: n for n, c in STOCKS}
CUSIPS = [c for _, c in STOCKS]
PLTR = "69608A108"
NAME[PLTR] = "PALANTIR TECHNOLOGIES INC"

FUNDS = [
    ("Aurora Ridge Capital LLC", "Boston"), ("Bluestem Partners LP", "Austin"),
    ("Copperline Investment Management", "Chicago"), ("Driftwood Advisors LLC", "Miami"),
    ("Evergreen Summit Asset Management", "Seattle"), ("Foxglove Capital Group", "New York"),
    ("Glacier Point Partners LLC", "San Francisco"), ("Highmark Holdings LP", "Dallas"),
    ("Ironwood Global Investors", "Greenwich"), ("Juniper Bay Capital LLC", "San Diego"),
    ("Kestrel Rock Management LP", "Denver"), ("Lantern Hill Advisors Inc", "Atlanta"),
]


def mk_acc():
    return f"{random.randint(1000000, 1999999):010d}-25-{random.randint(100000, 999999):06d}"


def line(acc, c, v, typ="SH", pc=""):
    price = random.randint(20, 400)
    return [acc, NAME[c], "COM" if typ == "SH" else "NOTE", c, v, max(1, v // price), typ, pc, "SOLE"]


holders = set(random.sample(range(12), 8))
non = [i for i in range(12) if i not in holders]
opt = {random.choice(non)} | set(random.sample(sorted(holders), 2))

cover, info = [], []
for i, (name, city) in enumerate(FUNDS):
    acc = mk_acc()
    cover.append([acc, "30-SEP-2025", name, city, f"028-{random.randint(10000, 19999)}"])
    for c in random.sample(CUSIPS, random.randint(10, 15)):
        info.append(line(acc, c, random.randint(1_000_000, 2_000_000_000)))
    if i in holders:
        v = random.randint(5_000_000, 3_000_000_000)
        if random.random() < 0.4:
            a = random.randint(v // 4, 3 * v // 4)
            info.append(line(acc, PLTR, a))
            info.append(line(acc, PLTR, v - a))
        else:
            info.append(line(acc, PLTR, v))
    if i in opt:
        info.append(line(acc, PLTR, random.randint(1_000_000_000, 4_000_000_000), "SH", random.choice(["Put", "Call"])))
    if random.random() < 0.3:
        info.append(line(acc, random.choice(CUSIPS), random.randint(10_000_000, 300_000_000), "PRN", ""))

random.shuffle(cover)
random.shuffle(info)
os.makedirs("2025-q3", exist_ok=True)
with open("2025-q3/COVERPAGE.tsv", "w", newline="") as f:
    w = csv.writer(f, delimiter=TAB, lineterminator="\n")
    w.writerow(["ACCESSION_NUMBER", "REPORTCALENDARORQUARTER", "FILINGMANAGER_NAME", "FILINGMANAGER_CITY", "FORM13FFILENUMBER"])
    w.writerows(cover)
with open("2025-q3/INFOTABLE.tsv", "w", newline="") as f:
    w = csv.writer(f, delimiter=TAB, lineterminator="\n")
    w.writerow(["ACCESSION_NUMBER", "INFOTABLE_SK", "NAMEOFISSUER", "TITLEOFCLASS", "CUSIP", "VALUE", "SSHPRNAMT", "SSHPRNAMTTYPE", "PUTCALL", "INVESTMENTDISCRETION"])
    for k, r in enumerate(info):
        w.writerow([r[0], 70000 + k] + r[1:])
