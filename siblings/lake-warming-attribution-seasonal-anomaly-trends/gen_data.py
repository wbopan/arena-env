import csv
import math
import random

random.seed(2219)
rows = []
for year in range(2001, 2025):
    for month in range(1, 13):
        seasonal = 9 + 8 * math.sin(2 * math.pi * (month - 3) / 12)
        slope = 0.085 if month in (12, 1, 2) else (0.045 if month in (3, 4, 5) else (0.01 if month in (6, 7, 8) else -0.055))
        temp = seasonal + slope * (year - 2001) + random.gauss(0, 0.43)
        missing = random.random() < 0.045
        rows.append([year, month, '' if missing else f'{temp:.5f}'])
random.shuffle(rows)
with open('monthly_water_temperature.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Year', 'Month', 'TempC'])
    writer.writerows(rows)
