import os
import math
import random

random.seed(4242)
os.makedirs("ocr", exist_ok=True)

ITEMS = ["MILO 1KG", "BREAD", "EGGS 10S", "RICE 5KG", "COFFEE", "SUGAR", "TEA BAGS", "NOODLE"]
STORES = ["KEDAI MAJU", "ACE MART", "SRI MURNI ENTERPRISE", "FAMILY STORE", "GOLDEN BAKERY"]
STYLES = ["grand", "totalrm", "totalcolonrm", "totalamount", "plain", "split", "amountdue", "none", "grand_big"]
HEADER = "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext"


def m(x):
    return f"{x:,.2f}"


for idx, style in enumerate(STYLES, start=1):
    names = random.sample(ITEMS, random.randint(2, 4))
    item_lines = []
    sub = 0.0
    for nm in names:
        if style == "grand_big":
            p = round(random.uniform(400, 900), 2)
            q = random.randint(2, 3)
        else:
            p = round(random.uniform(1, 60), 2)
            q = random.randint(1, 3)
        amt = round(q * p, 2)
        sub = round(sub + amt, 2)
        item_lines.append(f"{nm} {q} x {p:.2f} {m(amt)}")
    sst = round(sub * 0.06, 2)
    tot = round(sub + sst, 2)
    cash = float(math.ceil(tot / 10) * 10 + random.choice([0, 10, 20]))
    chg = round(cash - tot, 2)
    header = [random.choice(STORES), f"DATE: 2024-03-{idx + 3:02d}", f"RECEIPT NO: {random.randint(10000, 99999)}"]
    tl = [f"SUBTOTAL {m(sub)}", f"SST 6% {m(sst)}"]
    if style == "grand":
        tl += [f"TOTAL RM {m(sub)}", f"GRAND TOTAL {m(tot)}"]
    elif style == "totalrm":
        tl.append(f"TOTAL RM {m(tot)}")
    elif style == "totalcolonrm":
        tl += [f"NET TOTAL {m(sub)}", f"TOTAL: RM {m(tot)}"]
    elif style == "totalamount":
        tl.append(f"TOTAL AMOUNT {m(tot)}")
    elif style == "plain":
        tl.append(f"TOTAL {m(tot)}")
    elif style == "split":
        tl += ["TOTAL", f"RM {m(tot)}"]
    elif style == "amountdue":
        tl.append(f"AMOUNT DUE {m(tot)}")
    elif style == "grand_big":
        tl.append(f"GRAND TOTAL RM {m(tot)}")
    tl += [f"CASH {m(cash)}", f"CHANGE {m(chg)}"]

    blocks = [[[(w, random.uniform(55, 96)) for w in line.split()] for line in blk]
              for blk in (header, item_lines, tl)]

    if style in ("none", "plain", "amountdue"):
        noise = "TOTAL"
    else:
        noise = random.choice(["TOTAL", "9,999.99", "GRAND"])
    li = random.randrange(len(blocks[1]))
    blocks[1][li].append((noise, random.uniform(3, 29)))
    if style in ("grand", "totalrm", "split", "grand_big"):
        blocks[2][len(blocks[2]) - 3].append(("88.88", random.uniform(3, 29)))
    blocks[0][random.randrange(3)].append(("~", random.uniform(1, 20)))

    rows = [[1, 1, 0, 0, 0, 0, 0, 0, 600, 900, -1, ""]]
    top = 10
    for b, blk in enumerate(blocks, 1):
        rows.append([2, 1, b, 0, 0, 0, 10, top, 580, 30 * len(blk), -1, ""])
        rows.append([3, 1, b, 1, 0, 0, 10, top, 580, 30 * len(blk), -1, ""])
        for ln, words in enumerate(blk, 1):
            rows.append([4, 1, b, 1, ln, 0, 10, top, 580, 24, -1, ""])
            left = 10
            for wn, (t, c) in enumerate(words, 1):
                w = 12 * len(t)
                rows.append([5, 1, b, 1, ln, wn, left, top, w, 24, f"{c:.6f}", t])
                left += w + 12
            top += 30
    random.shuffle(rows)
    with open(f"ocr/r{idx:02d}.tsv", "w") as f:
        f.write(HEADER + "\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
