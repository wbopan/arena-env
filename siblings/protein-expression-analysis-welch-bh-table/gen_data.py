import random
import numpy as np
from openpyxl import Workbook

random.seed(7)
rng = np.random.default_rng(7)
lines = [("MDAMB468", "BREAST"), ("HCT116", "LARGE_INTESTINE"), ("A549", "LUNG"), ("MCF7", "BREAST"), ("PC3", "PROSTATE"), ("HELA", "CERVIX"), ("U2OS", "BONE")]
samples = []
for i in range(14):
    c, t = lines[i % len(lines)]
    samples.append(f"{c}_{t}_TenPx{i+1:02d}")
groups = ["Control"] * 6 + ["Treated"] * 6 + ["QC"] * 2
random.shuffle(groups)
proteins = ["P%05d" % x for x in random.sample(range(10000, 99999), 40)]
base = rng.normal(20, 2, 40)
data = base[:, None] + rng.normal(0, 0.4, (40, 14))
eff = np.zeros(40)
idx = rng.choice(40, 10, replace=False)
eff[idx] = rng.choice([-1, 1], 10) * rng.uniform(0.6, 2.0, 10)
tr = np.array([g == "Treated" for g in groups])
qc = np.array([g == "QC" for g in groups])
data[:, tr] += eff[:, None]
data[:, qc] += rng.normal(2.5, 1.0, (40, int(qc.sum())))
data = np.round(data, 3)

wb = Workbook()
ws = wb.active
ws.title = "Data"
ws.append(["Protein_ID"] + samples)
for p, row in zip(proteins, data):
    ws.append([p] + [float(v) for v in row])
ds = wb.create_sheet("Design")
ds.append(["Sample", "Group"])
order = list(range(14))
random.shuffle(order)
for i in order:
    ds.append([samples[i], groups[i]])
wb.save("protein_expression.xlsx")
