import json
import math
import random

random.seed(2219)

def matrix(tx, ty, tz, angle, scale):
    c, s = math.cos(angle) * scale, math.sin(angle) * scale
    return [c, s, 0, 0, -s, c, 0, 0, 0, 0, scale, 0, tx, ty, tz, 1]

positions = []
for i in range(5):
    positions.extend([round(random.uniform(-2, 2), 4), round(random.uniform(-2, 2), 4), round(random.uniform(-1, 1), 4)])
data = {
    'geometry': {'positions': positions, 'indices': [0, 1, 2, 0, 2, 3, 0, 3, 4]},
    'mesh_matrix': matrix(2.3, -1.4, 0.8, 0.31, 1.2),
    'instance_matrices': [matrix(random.uniform(-3, 3), random.uniform(-2, 2), random.uniform(-1, 1), random.uniform(-2, 2), random.uniform(0.6, 1.5)) for _ in range(4)],
}
with open('instances.json', 'w') as f:
    json.dump(data, f, indent=2)
