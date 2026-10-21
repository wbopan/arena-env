import json
import random

random.seed(7)
n = 5
cfg = {
    "n_sections": n,
    "EA": round(random.uniform(800, 1500), 1),
    "R": round(random.uniform(0.08, 0.12), 4),
    "fb": round(random.uniform(0.005, 0.02), 4),
    "dt": 0.01,
    "v0": round(random.uniform(0.5, 1.5), 3),
    "L": [round(random.uniform(0.5, 1.5), 3) for _ in range(n)],
    "J": [round(random.uniform(0.03, 0.08), 4) for _ in range(n)],
    "T_ref": [float(random.randint(15, 45)) for _ in range(n)],
}
with open("system_config.json", "w") as f:
    json.dump(cfg, f, indent=2)
