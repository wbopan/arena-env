import csv
import random

random.seed(7331)

SPEC = {
    "Creatinine": ((0.6, 9.0), [("mg/dL", 1.0), ("\u00b5mol/L", 1 / 88.4)]),
    "BUN": ((8.0, 90.0), [("mg/dL", 1.0), ("mmol/L", 2.8)]),
    "Hemoglobin": ((7.5, 16.5), [("g/dL", 1.0), ("g/L", 0.1), ("mmol/L", 1.611)]),
    "Calcium": ((7.5, 11.0), [("mg/dL", 1.0), ("mmol/L", 4.0), ("mEq/L", 2.0)]),
    "Glucose": ((65.0, 350.0), [("mg/dL", 1.0), ("mmol/L", 18.016)]),
    "Albumin": ((2.0, 5.0), [("g/dL", 1.0), ("g/L", 0.1)]),
}


def style_unit(u):
    if "\u00b5" in u:
        u = u.replace("\u00b5", random.choice(["\u00b5", "\u03bc", "u"]))
    k = random.random()
    if k < 0.25:
        u = u.lower()
    elif k < 0.4 and "\u00b5" not in u and "\u03bc" not in u:
        u = u.upper()
    if random.random() < 0.2:
        u = " " * random.randint(1, 2) + u + " " * random.randint(0, 2)
    return u


def style_value(v):
    s = f"{v:.{random.randint(1, 3)}f}"
    if random.random() < 0.3:
        s = s.replace(".", ",")
    return s


rows = []
for p in range(1, 51):
    for analyte, ((a, b), units) in SPEC.items():
        if random.random() > 0.85:
            continue
        true = random.uniform(a, b)
        if random.random() < 0.5:
            unit, fct = units[0]
        else:
            unit, fct = random.choice(units[1:])
        raw = true / fct
        rows.append([f"P{p:03d}", analyte, style_value(raw), style_unit(unit)])

for idx in random.sample(range(len(rows)), 14):
    kind = random.choice(["empty", "na", "nounit", "badunit"])
    if kind == "empty":
        rows[idx][2] = ""
    elif kind == "na":
        rows[idx][2] = "NA"
    elif kind == "nounit":
        rows[idx][3] = ""
    else:
        rows[idx][3] = random.choice(["IU/L", "mg", "?"])

# cross-analyte unit mistakes (unit not valid for that analyte)
for r in rows:
    if r[1] == "Creatinine" and random.random() < 0.05:
        r[3] = "g/L"

with open("measurements.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["patient_id", "analyte", "value", "unit"])
    w.writerows(rows)
