import json
from pathlib import Path
from itertools import product

P = Path('/root/work')

def distance(a, b):
    def axial(p):
        x, y = p
        return x - (y - y % 2)//2, y
    q, r = axial(a)
    s, t = axial(b)
    return max(abs(q-s), abs(r-t), abs(q+r-s-t))

def score(d, campus, holy):
    occupied = {tuple(campus), tuple(holy), tuple(d['city_center'])}
    scores = []
    for spot, kind in [(campus, 'CAMPUS'), (holy, 'HOLY_SITE')]:
        adjacent = [tile for tile in d['tiles'] if distance(spot, (tile['x'],tile['y'])) == 1]
        mountains = sum(tile['terrain'] == 'MOUNTAIN' for tile in adjacent)
        feature = 'JUNGLE' if kind == 'CAMPUS' else 'FOREST'
        pairs = sum(tile['feature'] == feature and (tile['x'],tile['y']) not in occupied for tile in adjacent)//2
        districts = sum(distance(spot, p) == 1 for p in occupied if p != tuple(spot))//2
        geothermal = 2*sum(tile['feature'] == 'GEOTHERMAL' for tile in adjacent) if kind == 'CAMPUS' else 0
        scores.append(mountains + pairs + districts + geothermal)
    return scores

def expected():
    d = json.loads((P/'pair_map.json').read_text())
    options = []
    for c, h in product(d['spots']['CAMPUS'], d['spots']['HOLY_SITE']):
        if c != h:
            b = score(d, c, h)
            options.append((sum(b), c, h, b))
    total, c, h, b = min(options, key=lambda v: (-v[0], v[1][1], v[1][0], v[2][1], v[2][0]))
    return {'placements':{'CAMPUS':c,'HOLY_SITE':h}, 'bonuses':{'CAMPUS':b[0],'HOLY_SITE':b[1]}, 'total':total}

def answer():
    return json.loads((P/'pair_answer.json').read_text())

def test_file():
    assert (P/'pair_answer.json').is_file()

def test_schema():
    a = answer()
    assert set(a) == {'placements','bonuses','total'}
    assert set(a['placements']) == set(a['bonuses']) == {'CAMPUS','HOLY_SITE'}
    assert all(isinstance(p, list) and len(p) == 2 and all(type(i) is int for i in p) for p in a['placements'].values())
    assert all(type(v) is int for v in a['bonuses'].values()) and type(a['total']) is int

def test_placements():
    assert answer()['placements'] == expected()['placements']

def test_bonuses():
    a, e = answer(), expected()
    assert a['bonuses'] == e['bonuses'] and a['total'] == e['total']
