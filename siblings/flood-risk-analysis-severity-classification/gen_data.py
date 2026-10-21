import csv
import math
import random

random.seed(20250401)

# (id, name, f, in_data, in_thresholds, special)
stations = [
    ("04101800", "St Joseph River at Niles", 0.5, True, True, "nomodmaj"),
    ("04097500", "St Joseph River at Three Rivers", 0.7, True, True, ""),
    ("04112500", "Red Cedar River at East Lansing", 0.9, True, True, ""),
    ("04115000", "Grand River at Ionia", 1.1, True, True, ""),
    ("04124000", "Manistee River near Sherman", 1.6, True, True, "noaction"),
    ("04142000", "Rifle River near Sterling", 0.4, True, True, "noflood"),
    ("04151500", "Cass River at Frankenmuth", 0.75, True, False, ""),
    ("04164000", "Clinton River near Fraser", 0.6, False, True, ""),
]

rows = []
thr_rows = []
for sid, name, f, in_data, in_thr, special in stations:
    base = random.uniform(3.0, 10.0)
    amp = random.uniform(2.0, 8.0)
    tp = random.uniform(40.0, 120.0)
    w = random.uniform(15.0, 40.0)
    if in_data:
        for h in range(0, 168, 4):
            day = 1 + h // 24
            hh = h % 24
            dt = "2025-04-%02d %02d:00" % (day, hh)
            val = base + amp * math.exp(-((h - tp) / w) ** 2) + random.gauss(0, 0.05)
            if random.random() < 0.04:
                rows.append((sid, dt, "", "Eqp"))
            else:
                rows.append((sid, dt, "%.2f" % val, "P"))
    if in_thr:
        flood = round(base + amp * f, 1)
        action = round(flood - 1.0, 1)
        moderate = round(flood + 0.2 * amp, 1)
        major = round(flood + 0.4 * amp, 1)
        if special == "nomodmaj":
            moderate = -9999
            major = -9999
        if special == "noaction":
            action = -9999
        if special == "noflood":
            flood = -9999
        thr_rows.append([sid, name, "MI", action, flood, moderate, major])

with open("gage_height_iv.rdb", "w") as fh:
    fh.write("# U.S. Geological Survey\n")
    fh.write("# Instantaneous values, parameter 00065 Gage height, feet\n")
    fh.write("# Synthetic data for April 1-7, 2025\n")
    fh.write("agency_cd\tsite_no\tdatetime\ttz_cd\t00065\t00065_cd\n")
    fh.write("5s\t15s\t20d\t6s\t14n\t10s\n")
    for sid, dt, v, cd in rows:
        fh.write("USGS\t%s\t%s\tEDT\t%s\t%s\n" % (sid, dt, v, cd))

with open("nws_thresholds.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["usgs id", "location name", "state", "action stage", "flood stage", "moderate flood stage", "major flood stage"])
    for r in thr_rows:
        w.writerow(r + [""])
