import json
import random

random.seed(20240611)
ids = random.sample(range(100, 1000), 14)
stations = []
for sid in ids:
    cap = random.randint(15, 40)
    stations.append({
        'id': sid,
        'latitude': round(40.70 + random.random() * 0.10, 6),
        'longitude': round(-74.03 + random.random() * 0.10, 6),
        'initial_bikes': random.randint(0, cap),
        'station_capacity': cap,
        'net_rebalancing_target': random.randint(-8, 8),
    })
data = {
    'vehicle_count': 3,
    'vehicle_capacity': 15,
    'penalty_weight': 2.5,
    'depot': {'latitude': 40.7505, 'longitude': -73.9934},
    'stations': stations,
}
vehicles = []
for vid in range(1, 4):
    chosen = random.sample(stations, random.randint(3, 6))
    stops = []
    for s in chosen:
        t = s['net_rebalancing_target']
        q = random.randint(1, abs(t) + 4)
        if t > 0 or (t == 0 and random.random() < 0.5):
            stops.append({'station_id': s['id'], 'bikes_picked_up': q, 'bikes_dropped_off': 0})
        else:
            stops.append({'station_id': s['id'], 'bikes_picked_up': 0, 'bikes_dropped_off': q})
    vehicles.append({'vehicle_id': vid, 'start_load': random.randint(0, 6), 'stops': stops})
with open('data.json', 'w') as f:
    json.dump(data, f, indent=2)
with open('plan.json', 'w') as f:
    json.dump({'vehicles': vehicles}, f, indent=2)
