import csv
import json
import random

random.seed(7182)
cities = ['Cleveland', 'Toledo', 'Akron', 'Columbus', 'Dayton', 'Cincinnati']
with open('cities.txt', 'w') as f:
    for city in cities:
        f.write(f'Ohio\t{city}\n')
    f.write('Michigan\tDetroit\n')
with open('trip.json', 'w') as f:
    json.dump({'start': 'Cleveland', 'end': 'Cincinnati', 'stops': ['Toledo', 'Akron', 'Columbus', 'Dayton']}, f)
with open('distance.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['origin', 'destination', 'duration', 'distance'])
    w.writeheader()
    for a in cities:
        for b in cities:
            if a == b:
                continue
            km = random.randint(75, 390)
            minutes = km + random.randint(12, 105)
            w.writerow({'origin': a, 'destination': b, 'duration': f'{minutes // 60} hours {minutes % 60} mins', 'distance': f'{km} km'})
