import json
import random

random.seed(59216)
cases = []
for i in range(4):
    cases.append({
        'case_id': f'F{i+1}',
        'detuning': round(random.uniform(-0.9, 0.9), 6),
        'rabi': round(random.uniform(0.3, 1.25), 6),
        'gamma_down': round(random.uniform(0.45, 1.3), 6),
        'gamma_phi': round(random.uniform(0.03, 0.4), 6),
    })
with open('fluorescence_cases.json', 'w') as f:
    json.dump({'delays': [0.0, 0.25, 0.75, 1.5, 3.0], 'cases': cases}, f, indent=2)
