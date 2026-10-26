#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_modes.py <<'PY'
import csv


def load(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))

requests = load('requests.csv')
roads = load('driving.csv')
flights = load('flights.csv')
with open('modes.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['date', 'origin', 'destination', 'mode', 'service_id', 'cost_usd', 'duration_min'])
    for req in requests:
        options = []
        for road in roads:
            if road['origin'] != req['origin'] or road['destination'] != req['destination']:
                continue
            hours, rest = road['duration'].split(' hours ')
            minutes = int(hours) * 60 + int(rest.split()[0])
            cost = int(road['distance'].split()[0]) * 15 // 100 + int(road['toll_usd'])
            if minutes <= int(req['max_minutes']):
                options.append((cost, minutes, 'drive', 'SELF_DRIVE'))
        for flight in flights:
            if (flight['FlightDate'], flight['OriginCityName'], flight['DestCityName']) != (req['date'], req['origin'], req['destination']):
                continue
            minutes = int(flight['ActualElapsedTime'])
            if minutes <= int(req['max_minutes']):
                options.append((2 * int(flight['Price']), minutes, 'flight', flight['Flight Number']))
        cost, minutes, mode, service = min(options)
        w.writerow([req['date'], req['origin'], req['destination'], mode, service, cost, minutes])
PY
python /tmp/solve_modes.py
