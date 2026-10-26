import csv
import random

random.seed(8407)
trips = [('2022-04-11', 'Cleveland', 'Columbus', 210), ('2022-04-12', 'Columbus', 'Cincinnati', 340), ('2022-04-13', 'Cincinnati', 'Dayton', 260), ('2022-04-14', 'Dayton', 'Toledo', 275), ('2022-04-15', 'Toledo', 'Cleveland', 320)]
with open('requests.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['date', 'origin', 'destination', 'max_minutes'])
    for trip in trips:
        w.writerow(trip)
with open('driving.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['origin', 'destination', 'duration', 'distance', 'toll_usd'])
    for i, (_, origin, destination, _) in enumerate(trips):
        minutes = 380 if i == 0 else random.randint(155, 280)
        km = random.randint(230, 560)
        toll = random.randint(12, 90)
        w.writerow([origin, destination, f'{minutes // 60} hours {minutes % 60} mins', f'{km} km', toll])
with open('flights.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['Flight Number', 'Price', 'DepTime', 'ArrTime', 'ActualElapsedTime', 'FlightDate', 'OriginCityName', 'DestCityName', 'Distance'])
    for i, (date, origin, destination, _) in enumerate(trips):
        for j in range(3):
            price = random.randint(33, 140) if i != 1 else random.randint(155, 205)
            w.writerow([f'Q{i + 1}{j + 1:02}', price, '0900', '1200', random.randint(65, 195), date, origin, destination, random.randint(90, 390)])
    w.writerow(['DECOY', 1, '0900', '1000', 40, '2022-04-20', trips[0][1], trips[0][2], 100])
