import json
import random

random.seed(424242)
NT, NV = 20, 5
coords = [(15, 15)] + [(random.randint(0, 30), random.randint(0, 30)) for _ in range(2 * NT)]
n = len(coords)
M = [[0 if i == j else abs(coords[i][0] - coords[j][0]) + abs(coords[i][1] - coords[j][1]) + 2
      for j in range(n)] for i in range(n)]
with open("t_matrix.csv", "w") as f:
    for row in M:
        f.write(",".join(map(str, row)) + "\n")

cfg = {"capacity": 4, "service_time": 3, "shift_duration": 300, "max_ride_time": 75, "depot_node": 0}
trips = [{"trip_id": "T%02d" % (k + 1), "pickup_node": 2 * k + 1, "dropoff_node": 2 * k + 2,
          "load": random.choice([1, 1, 2, 3])} for k in range(NT)]

unassigned = random.randrange(NT)
idx = [k for k in range(NT) if k != unassigned]
random.shuffle(idx)
groups = [idx[v::NV] for v in range(NV)]
routes = []
for v, g in enumerate(groups):
    pending = list(g)
    onboard = []
    seq = []
    while pending or onboard:
        if pending and (not onboard or (len(onboard) < 2 and random.random() < 0.6)):
            k = pending.pop(0)
            onboard.append(k)
            seq.append(2 * k + 1)
        else:
            k = onboard.pop(random.randrange(len(onboard)))
            seq.append(2 * k + 2)
    routes.append({"vehicle_id": "V%d" % (v + 1), "start_time": random.choice(list(range(360, 601, 30))),
                   "node_sequence": seq})

# precedence error on V1: move first trip's dropoff to the front
seq0 = routes[0]["node_sequence"]
k0 = (seq0[0] - 1) // 2
seq0.remove(2 * k0 + 2)
seq0.insert(0, 2 * k0 + 2)

arr = {}
for r in routes:
    t = r["start_time"]
    prev = 0
    for nd in r["node_sequence"]:
        t += M[prev][nd]
        arr[nd] = t
        t += cfg["service_time"]
        prev = nd


def tw(nd):
    if nd in arr:
        a = arr[nd]
        return [a - random.randint(5, 20), a + random.randint(10, 30)]
    return [480, 600]


for tr in trips:
    tr["pickup_tw"] = tw(tr["pickup_node"])
    tr["dropoff_tw"] = tw(tr["dropoff_node"])

# window violation on V2
d_nodes = [nd for nd in routes[1]["node_sequence"] if nd % 2 == 0]
nd = random.choice(d_nodes)
tr = trips[(nd - 1) // 2]
hi = arr[nd] - random.randint(1, 5)
tr["dropoff_tw"] = [min(tr["dropoff_tw"][0], hi - 10), hi]

# forced waiting on V3
p_nodes = [nd for nd in routes[2]["node_sequence"] if nd % 2 == 1]
nd = random.choice(p_nodes)
tr = trips[(nd - 1) // 2]
lo = arr[nd] + random.randint(6, 14)
tr["pickup_tw"] = [lo, max(tr["pickup_tw"][1], lo + 5)]

reqs = []
k = 0
r = 1
while k < NT:
    s = min(random.choice([1, 1, 2, 2, 3]), NT - k)
    reqs.append({"request_id": "R%02d" % r, "trips": trips[k:k + s]})
    k += s
    r += 1

with open("requests.json", "w") as f:
    json.dump(reqs, f, indent=1)
with open("config.json", "w") as f:
    json.dump(cfg, f, indent=1)
with open("plan.json", "w") as f:
    json.dump({"routes": routes}, f, indent=1)
