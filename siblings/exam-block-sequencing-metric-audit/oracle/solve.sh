#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_audit.py <<'EOF'
import csv, json
inst = json.load(open('instance.json'))
pair = {(r['block_i'], r['block_j']): int(r['count']) for r in csv.DictReader(open('pair_counts.csv'))}
trip = {(r['block_i'], r['block_j'], r['block_k']): int(r['count']) for r in csv.DictReader(open('triplet_counts.csv'))}
at = {r['slot']: r['block'] for r in csv.DictReader(open('schedule.csv'))}
order = inst['slot_order']
nxt = {order[i]: order[i + 1] for i in range(len(order) - 1)}
def seq(s, k):
    out = [s]
    for _ in range(k):
        out.append(nxt[out[-1]])
    return [at[x] for x in out]
em = sum(pair.get(tuple(seq(s, 1)), 0) for s in inst['eve_morn_start'])
ot = sum(pair.get(tuple(seq(s, 1)), 0) for s in inst['other_b2b_start'])
sd = sum(trip.get(tuple(seq(s, 2)), 0) for s in inst['triple_day_start'])
cd = sum(trip.get(tuple(seq(s, 2)), 0) for s in inst['triple_24_start'])
z = 0
for s in inst['four_start']:
    q = seq(s, 3)
    z += trip.get((q[0], q[1], q[3]), 0) + trip.get((q[0], q[2], q[3]), 0)
res = {'objective': em + ot + 10 * sd + 10 * cd + 5 * z,
       'eve_morn_b2b_count': em, 'other_b2b_count': ot,
       'same_day_triple_count': sd, 'cross_day_triple_count': cd,
       'z_three_in_four_count': z}
json.dump(res, open('metrics.json', 'w'), indent=2)
print(res)
EOF
python3 /tmp/solve_audit.py
