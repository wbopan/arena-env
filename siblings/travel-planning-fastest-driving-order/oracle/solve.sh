#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_route.py <<'PY'
import csv
import itertools
import json

trip = json.load(open('trip.json'))
edges = {}
with open('distance.csv', newline='') as f:
    for row in csv.DictReader(f):
        hour, rest = row['duration'].split(' hours ')
        edges[row['origin'], row['destination']] = (int(hour) * 60 + int(rest.split()[0]), int(row['distance'].split()[0]))
options = []
for stops in itertools.permutations(trip['stops']):
    route = [trip['start'], *stops, trip['end']]
    pairs = list(zip(route, route[1:]))
    options.append(((sum(edges[p][0] for p in pairs), sum(edges[p][1] for p in pairs), stops), route, pairs))
_, route, pairs = min(options)
legs = [{'origin': a, 'destination': b, 'distance_km': edges[a, b][1], 'duration_min': edges[a, b][0]} for a, b in pairs]
with open('route.json', 'w') as f:
    json.dump({'ordered_city_names': route, 'legs': legs, 'total_distance_km': sum(x['distance_km'] for x in legs), 'total_duration_min': sum(x['duration_min'] for x in legs)}, f)
PY
python /tmp/solve_route.py
