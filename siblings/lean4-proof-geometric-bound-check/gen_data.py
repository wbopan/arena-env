import csv
import random
from fractions import Fraction as F

random.seed(777)


def fs(x):
    return f"{x.numerator}/{x.denominator}"


rows = []
for i in range(40):
    s0 = F(random.randint(-5, 10), random.randint(1, 6))
    a = F(random.randint(1, 9), random.randint(1, 5))
    q = random.randint(2, 12)
    p = random.randint(1, q - 1)
    r = F(p, q)
    L = s0 + a * r / (1 - r)
    mode = i % 4
    if mode == 0:
        B = L
    elif mode == 1:
        B = L + F(random.randint(1, 20), random.randint(50, 500))
    elif mode == 2:
        k = random.randint(1, 25)
        B = L - a * r ** (k + 1) / (1 - r) * F(random.randint(1, 19), 10)
    else:
        B = s0 - F(random.randint(0, 3), 7)
    rows.append([f"seq{i:02d}", fs(s0), fs(a), fs(r), fs(B)])
random.shuffle(rows)

with open("sequences.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["id", "s0", "a", "r", "bound"])
    w.writerows(rows)
