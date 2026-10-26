import json
import random

random.seed(7291)
opening_length = random.randint(10, 16)
energies = [random.randint(3, 8) for _ in range(opening_length)]
energies += [random.randint(68, 125) for _ in range(55 - opening_length)]
for start in (27, 43):
    energies[start:start + 2] = [random.randint(2, 7) for _ in range(2)]
with open('energies.json', 'w') as f:
    json.dump({'sample_rate': 16000, 'window_seconds': 1,
               'total_seconds': len(energies), 'energies': energies}, f, indent=2)
