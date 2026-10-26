import json
import random

random.seed(2741)
features = [None, None, 'FOREST', 'JUNGLE', 'GEOTHERMAL']
tiles = []
for y in range(6):
    for x in range(7):
        tiles.append({'x': x, 'y': y, 'terrain': 'MOUNTAIN' if random.random() < 0.12 else 'PLAINS', 'feature': random.choice(features)})
campus = [[2,1], [3,1], [2,2], [4,3]]
holy = [[1,2], [3,2], [4,2], [3,4]]
for t in tiles:
    if [t['x'],t['y']] in campus + holy + [[3,3]]:
        t['terrain'] = 'PLAINS'
with open('pair_map.json','w') as f:
    json.dump({'city_center':[3,3], 'tiles':tiles, 'spots':{'CAMPUS':campus, 'HOLY_SITE':holy}}, f)
