import json
import random

random.seed(81703)
runs = []
for i in range(3):
    runs.append({
        'case_id': f'R{i+1}',
        'omega1': round(random.uniform(-0.5, 0.7), 6),
        'omega2': round(random.uniform(-0.6, 0.4), 6),
        'exchange': round(random.uniform(0.18, 0.85), 6),
        'gamma1': round(random.uniform(0.08, 0.36), 6),
        'gamma2': round(random.uniform(0.06, 0.31), 6),
        'gamma_phi': round(random.uniform(0.04, 0.29), 6),
    })
with open('qubit_runs.json', 'w') as f:
    json.dump({'times': [0.0, 0.35, 0.9, 1.7, 2.8], 'runs': runs}, f, indent=2)
