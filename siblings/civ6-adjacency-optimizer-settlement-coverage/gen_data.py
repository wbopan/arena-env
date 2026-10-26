import json
import random

random.seed(6124)
w, h = 9, 8
tiles = [{'x': x, 'y': y, 'weight': random.randrange(0, 8)} for y in range(h) for x in range(w)]
candidates = [[x, y] for x, y in [(1, 1), (3, 2), (6, 2), (2, 5), (5, 5), (7, 6)]]
with open('settlement.json', 'w') as f:
    json.dump({'width': w, 'height': h, 'tiles': tiles, 'candidates': candidates}, f)
