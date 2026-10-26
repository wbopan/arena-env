#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_sights.py <<'PY'
import csv
import itertools
import json

visit = json.load(open('visit.json'))
with open('attractions.csv', newline='') as f:
    rows = list(csv.DictReader(f))
groups = [[r for r in rows if r['City'] == city] for city in visit['cities']]
choices = []
for picks in itertools.product(*groups):
    fee = sum(int(r['AdmissionUSD']) for r in picks)
    if fee > visit['budget_usd'] or len({r['Category'] for r in picks}) != len(picks):
        continue
    score = sum(int(r['Score']) for r in picks)
    choices.append(((-score, fee, tuple(r['Name'] for r in picks)), picks))
picks = min(choices, key=lambda x: x[0])[1]
selected = [{'city': r['City'], 'attraction': r['Name'], 'category': r['Category'], 'admission_usd': int(r['AdmissionUSD']), 'score': int(r['Score'])} for r in picks]
with open('sights.json', 'w') as f:
    json.dump({'selected': selected, 'total_admission_usd': sum(r['admission_usd'] for r in selected), 'total_score': sum(r['score'] for r in selected)}, f)
PY
python /tmp/solve_sights.py
