import csv
import os
import random

random.seed(20250930)
TAB = chr(9)

PRE = ["ALPINE", "BOREAL", "CASCADE", "DELTA", "EMBER", "FALCON", "GRANITE", "HARBOR"]
SUF = ["SYSTEMS INC", "HOLDINGS CORP", "ENERGY CO", "FOODS INC", "BANCORP"]
ALNUM = "0123456789ABCDEFGHJKLMNPRSTUVWXYZ"
used = set()


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


def mk_acc():
    return f"{random.randint(1000000, 1999999):010d}-25-{random.randint(100000, 999999):06d}"


def lines(acc, hold, extras):
    out = []
    for c, v in hold.items():
        price = random.randint(20, 400)
        if v > 2_000_000 and random.random() < 0.35:
            a = random.randint(v // 4, 3 * v // 4)
            parts = [a, v - a]
        else:
            parts = [v]
        for p in parts:
            out.append([acc, NAME[c], "COM", c, p, max(1, p // price), "SH", "", "SOLE"])
    for c, v, typ, pc in extras:
        out.append([acc, NAME[c], "COM" if typ == "SH" else "NOTE", c, v, max(1, v // 100), typ, pc, "SOLE"])
    return out


def rand_hold(n, lo, hi):
    return {c: random.randint(lo, hi) for c in random.sample(CUSIPS, n)}


OTHERS = [
    ("Berkshire Capital Holdings Inc", "Boston", "028-11201"),
    ("Northwind Asset Management LLC", "Chicago", "028-13377"),
    ("Quarry Lane Partners LP", "New York", "028-15002"),
    ("Silver Birch Advisors LLC", "Denver", "028-16840"),
    ("Tidewater Capital Group", "Charleston", "028-17123"),
]

bh2 = rand_hold(15, 5_000_000, 5_000_000_000)
b2c = list(bh2)
kept, exited = b2c[:11], b2c[11:]
bh3 = {}
for i, c in enumerate(kept):
    f = random.uniform(1.2, 1.8) if i < 4 else random.uniform(0.5, 1.5)
    bh3[c] = int(bh2[c] * f)
rest = [c for c in CUSIPS if c not in bh2]
random.shuffle(rest)
for c in rest[:3]:
    bh3[c] = random.randint(50_000_000, 3_000_000_000)
spare = rest[3:]
bh_extra2 = [(spare[0], random.randint(100_000_000, 900_000_000), "SH", "Call"),
             (spare[1], random.randint(100_000_000, 900_000_000), "PRN", "")]
bh_extra3 = [(exited[0], random.randint(100_000_000, 900_000_000), "SH", "Put"),
             (spare[2], random.randint(100_000_000, 900_000_000), "SH", "Call"),
             (spare[1], random.randint(100_000_000, 900_000_000), "PRN", "")]


def write_q(folder, period, filers):
    os.makedirs(folder, exist_ok=True)
    cover, info = [], []
    for name, city, fnum, acc, hold, extras in filers:
        cover.append([acc, period, name, city, fnum])
        info.extend(lines(acc, hold, extras))
    random.shuffle(cover)
    random.shuffle(info)
    with open(os.path.join(folder, "COVERPAGE.tsv"), "w", newline="") as f:
        w = csv.writer(f, delimiter=TAB, lineterminator="\n")
        w.writerow(["ACCESSION_NUMBER", "REPORTCALENDARORQUARTER", "FILINGMANAGER_NAME", "FILINGMANAGER_CITY", "FORM13FFILENUMBER"])
        w.writerows(cover)
    with open(os.path.join(folder, "INFOTABLE.tsv"), "w", newline="") as f:
        w = csv.writer(f, delimiter=TAB, lineterminator="\n")
        w.writerow(["ACCESSION_NUMBER", "INFOTABLE_SK", "NAMEOFISSUER", "TITLEOFCLASS", "CUSIP", "VALUE", "SSHPRNAMT", "SSHPRNAMTTYPE", "PUTCALL", "INVESTMENTDISCRETION"])
        for i, r in enumerate(info):
            w.writerow([r[0], 50000 + i] + r[1:])


for folder, period, bhname, bh, bhx in [
    ("2025-q2", "30-JUN-2025", "BERKSHIRE HATHAWAY INC", bh2, bh_extra2),
    ("2025-q3", "30-SEP-2025", "Berkshire Hathaway Inc", bh3, bh_extra3),
]:
    filers = [(bhname, "Omaha", "028-04545", mk_acc(), bh, bhx)]
    for name, city, fnum in OTHERS:
        hold = rand_hold(random.randint(10, 14), 1_000_000, 2_000_000_000)
        ex = [(random.choice(CUSIPS), random.randint(1_000_000, 500_000_000), "SH", random.choice(["Put", "Call"]))]
        filers.append((name, city, fnum, mk_acc(), hold, ex))
    write_q(folder, period, filers)
