import json
import random

random.seed(4217)

T = 6.0
x0 = round(random.uniform(-20, 20), 2)
y0 = round(random.uniform(-15, 15), 2)
W = round(random.uniform(84, 110), 2)
H = round(random.uniform(66, 90), 2)
x1 = x0 + W
y1 = y0 + H
ents = []


def line(layer, a, b):
    ents.append(('LINE', layer, a, b))


def rect(layer, a, b, c, d):
    pts = [(a, b), (c, b), (c, d), (a, d)]
    for i in range(4):
        line(layer, pts[i], pts[(i + 1) % 4])


line('WALL', (x0 - T, y0 - T), (x0 - T, y1 + T))
line('WALL', (x0, y0), (x0, y1))
line('WALL', (x1 + T, y0 - T), (x1 + T, y1 + T))
line('WALL', (x1, y0), (x1, y1))
line('WALL', (x0 - T, y1 + T), (x1 + T, y1 + T))
line('WALL', (x0, y1), (x1, y1))

dw = round(random.uniform(30, 37), 2)
ds = round(x0 + random.uniform(4, W - dw - 4), 2)
de = ds + dw
line('WALL', (x0, y0), (ds, y0))
line('WALL', (de, y0), (x1, y0))
line('WALL', (x0 - T, y0 - T), (ds, y0 - T))
line('WALL', (de, y0 - T), (x1 + T, y0 - T))
line('DOOR', (ds, y0), (de, y0))
line('DOOR', (ds, y0), (ds, y0 + dw))
ents.append(('ARC', 'DOOR', (ds, y0), dw, 0.0, 90.0))

off = round(random.uniform(14, 20), 2)
cx = x0 + off
rect('WC', cx - 9, y1 - 28, cx + 9, y1)
ents.append(('CIRCLE', 'WC', (cx, y1 - 17), 7.0))

rect('TUB', x1 - 30, y1 - 60, x1, y1)
ents.append(('ARC', 'TUB', (x1 - 15, y1 - 30), 11.0, 200.0, 340.0))

ls = round(random.uniform(36, 48), 2)
line('GRABBAR', (x0 + 1.5, y1 - 2 - ls), (x0 + 1.5, y1 - 2))
lr = round(random.uniform(30, 42), 2)
s = round(random.uniform(2, 16), 2)
line('GRABBAR', (x0 + s, y1 - 1.5), (x0 + s + lr, y1 - 1.5))

D = random.choice([60.0, 60.0, 58.0])
tcx = round(random.uniform(x0 + D / 2, x1 - D / 2), 2)
tcy = round(random.uniform(y0 + D / 2, y1 - D / 2), 2)
ents.append(('CIRCLE', 'CLEARANCE', (tcx, tcy), D / 2))
ents.append(('TEXT', 'ANNO', (x0 + 5, y0 + 5), 'TOILET ROOM 1'))
random.shuffle(ents)


def f(v):
    return f'{v:.4f}'


out = ['0', 'SECTION', '2', 'HEADER', '9', '$INSUNITS', '70', '1', '0', 'ENDSEC',
       '0', 'SECTION', '2', 'ENTITIES']
for e in ents:
    kind, layer = e[0], e[1]
    out += ['0', kind, '8', layer]
    if kind == 'LINE':
        out += ['10', f(e[2][0]), '20', f(e[2][1]), '30', '0.0',
                '11', f(e[3][0]), '21', f(e[3][1]), '31', '0.0']
    elif kind == 'CIRCLE':
        out += ['10', f(e[2][0]), '20', f(e[2][1]), '30', '0.0', '40', f(e[3])]
    elif kind == 'ARC':
        out += ['10', f(e[2][0]), '20', f(e[2][1]), '30', '0.0', '40', f(e[3]),
                '50', f(e[4]), '51', f(e[5])]
    elif kind == 'TEXT':
        out += ['10', f(e[2][0]), '20', f(e[2][1]), '30', '0.0', '40', '2.0', '1', e[3]]
out += ['0', 'ENDSEC', '0', 'EOF']
with open('ada_bath_plan.dxf', 'w') as fh:
    fh.write('\n'.join(out) + '\n')

rules = {
    'unit': 'in',
    'rules': {
        'door_clear_width_min': {'element': 'D1', 'min': 32.0},
        'toilet_centerline_from_side_wall_range': {'element': 'WC1', 'min': 16.0, 'max': 18.0},
        'side_grab_bar_length_min': {'element': 'GB_SIDE', 'min': 42.0},
        'rear_grab_bar_length_min': {'element': 'GB_REAR', 'min': 36.0},
        'rear_grab_bar_toilet_centerline_span': {'element': 'GB_REAR'},
        'turning_circle_diameter_min': {'element': 'bathroom_1', 'min': 60.0},
        'turning_circle_fit_usable_floor': {'element': 'bathroom_1', 'wall_offset': 1.0,
                                            'blocking_layers': ['TUB']},
    },
}
with open('ada_rules.json', 'w') as fh:
    json.dump(rules, fh, indent=2)
