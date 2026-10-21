import csv
import random

random.seed(20240611)

# name, min, max, unit, alt factors, true-value generation range
FEATS = [
    ("Serum_Creatinine", 0.2, 20.0, "mg/dL", [0.0113], (0.5, 12.0)),
    ("Hemoglobin", 3.0, 20.0, "g/dL", [0.1], (7.0, 17.0)),
    ("Glucose", 20.0, 800.0, "mg/dL", [18.02], (60.0, 300.0)),
    ("Total_Cholesterol", 50.0, 500.0, "mg/dL", [38.67], (120.0, 320.0)),
    ("Triglycerides", 30.0, 2000.0, "mg/dL", [88.5], (50.0, 600.0)),
    ("Uric_Acid", 1.0, 20.0, "mg/dL", [0.0168], (3.0, 12.0)),
    ("Prealbumin", 5.0, 50.0, "mg/dL", [0.1, 100.0], (10.0, 40.0)),
]


def fmt(v):
    k = random.random()
    if k < 0.15:
        s = f"{v:.4e}"
    elif k < 0.35:
        s = f"{v:.{random.randint(1, 4)}f}".replace(".", ",")
    else:
        s = f"{v:.{random.randint(1, 4)}f}"
    if random.random() < 0.15:
        s = " " * random.randint(1, 3) + s + " " * random.randint(0, 2)
    return s


with open("lab_reference.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["feature", "min", "max", "unit", "alt_factors"])
    for name, lo, hi, unit, facs, _ in FEATS:
        w.writerow([name, lo, hi, unit, ";".join(repr(x) for x in facs)])

rows = []
for i in range(1, 61):
    row = [f"P{i:03d}"]
    for name, lo, hi, unit, facs, (a, b) in FEATS:
        true = round(random.uniform(a, b), 2)
        if random.random() < 0.35:
            fct = random.choice(facs)
            raw = round(true / fct, 4)
        else:
            raw = true
        row.append(fmt(raw))
    rows.append(row)

for idx in random.sample(range(len(rows)), 9):
    col = random.randint(1, len(FEATS))
    rows[idx][col] = random.choice(["", "NA", "NaN"])

with open("labs_wide.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["patient_id"] + [x[0] for x in FEATS])
    w.writerows(rows)
