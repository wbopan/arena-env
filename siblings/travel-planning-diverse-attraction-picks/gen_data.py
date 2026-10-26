import csv
import json
import random

random.seed(39041)
cities = ['Cleveland', 'Columbus', 'Cincinnati']
categories = ['Museum', 'Park', 'Gallery', 'History']
with open('visit.json', 'w') as f:
    json.dump({'cities': cities, 'budget_usd': 63}, f)
with open('attractions.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['Name', 'City', 'Category', 'AdmissionUSD', 'Score'])
    w.writeheader()
    for i, city in enumerate(cities):
        for j in range(6):
            category = categories[i] if j == 0 else random.choice(categories)
            admission = random.randint(6, 11) if j == 0 else random.randint(9, 39)
            w.writerow({'Name': f'{city} Site {j + 1}', 'City': city, 'Category': category, 'AdmissionUSD': admission, 'Score': random.randint(4, 22)})
