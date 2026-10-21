import csv
import numpy as np
import openpyxl

rng = np.random.default_rng(2024)
years = list(range(1980, 2025))
n = len(years)
t = np.arange(n)
c = np.zeros(n)
for i in range(1, n):
    c[i] = 0.6 * c[i - 1] + rng.normal(0, 0.02)
lpce = np.log(3000) + 0.025 * t + 0.35 * c + rng.normal(0, 0.004, n) + 0.003 * np.sin(t / 3.0)
lpfi = np.log(800) + 0.03 * t + 2.2 * c + rng.normal(0, 0.02, n)

months = [(y, m) for y in years for m in range(1, 13) if not (y == 2024 and m > 9)]
lc = np.log(82.4)
infl = 0.003
cpi_vals = []
for _ in months:
    infl = 0.003 + 0.85 * (infl - 0.003) + rng.normal(0, 0.0015)
    lc += infl
    cpi_vals.append(round(float(np.exp(lc)), 3))

with open("cpi_monthly.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["observation_date", "CPIAUCSL"])
    for (y, m), v in zip(months, cpi_vals):
        w.writerow([f"{y}-{m:02d}-01", v])

cpi_ann = {}
for (y, m), v in zip(months, cpi_vals):
    cpi_ann.setdefault(y, []).append(v)
cpi_ann = {y: float(np.mean(v)) for y, v in cpi_ann.items()}

qlab = ["I", "II", "III", "IV"]


def build(lreal, fname, title, headers, share):
    nom = {y: float(np.exp(lreal[i]) * cpi_ann[y] / 100.0) for i, y in enumerate(years)}
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Table"
    ws.append([title])
    ws.append(["[Billions of dollars; quarterly data at seasonally adjusted annual rates]"])
    ws.append(headers)
    for y in years[:-1]:
        tot = round(nom[y], 1)
        a = round(tot * share, 1)
        ws.append([y, tot, a, round(tot - a, 1)])
    for y, nq in ((2023, 4), (2024, 3)):
        offs = [-0.012, -0.004, 0.004, 0.012]
        for q in range(nq):
            tot = round(nom[y] * (1 + offs[q] + rng.normal(0, 0.003)), 1)
            a = round(tot * share, 1)
            ws.append([f"{y}: {qlab[q]}", tot, a, round(tot - a, 1)])
    ws.append(["Source: Department of Commerce (Bureau of Economic Analysis)."])
    wb.save(fname)


build(lpce, "pce_nominal.xlsx", "Table B-10. Personal consumption expenditures, 1980-2024",
      ["Year or quarter", "Personal consumption expenditures", "Goods", "Services"], 0.36)
build(lpfi, "pfi_nominal.xlsx", "Table B-12. Private fixed investment, 1980-2024",
      ["Year or quarter", "Total private fixed investment", "Nonresidential", "Residential"], 0.74)
