#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_ada.py <<'EOF'
import json
import math

raw = [l.strip() for l in open('ada_bath_plan.dxf').read().splitlines()]
pairs = list(zip(raw[0::2], raw[1::2]))
i = pairs.index(('2', 'ENTITIES'))
ents = []
cur = None
for c, v in pairs[i + 1:]:
    if c == '0':
        if cur:
            ents.append(cur)
        if v == 'ENDSEC':
            break
        cur = {'t': v}
    else:
        cur.setdefault(c, v)


def segs(layer):
    return [(float(e['10']), float(e['20']), float(e['11']), float(e['21']))
            for e in ents if e['t'] == 'LINE' and e.get('8') == layer]


def ext(ss):
    xs = [p for s in ss for p in (s[0], s[2])]
    ys = [p for s in ss for p in (s[1], s[3])]
    return min(xs), min(ys), max(xs), max(ys)


rules = json.load(open('ada_rules.json'))['rules']
w = segs('WALL')
vx = sorted({round(s[0], 4) for s in w if abs(s[0] - s[2]) < 1e-6})
hy = sorted({round(s[1], 4) for s in w if abs(s[1] - s[3]) < 1e-6})
xmin, xmax, ymin, ymax = vx[1], vx[-2], hy[1], hy[-2]
op = [s for s in segs('DOOR') if abs(s[1] - s[3]) < 1e-6][0]
dw = abs(op[2] - op[0])
a, _, b, _ = ext(segs('WC'))
cx = (a + b) / 2
cl = min(cx - xmin, xmax - cx)
gb = segs('GRABBAR')
side = [s for s in gb if abs(s[0] - s[2]) < 1e-6][0]
rear = [s for s in gb if abs(s[1] - s[3]) < 1e-6][0]
ls = abs(side[3] - side[1])
lr = abs(rear[2] - rear[0])
c = [e for e in ents if e['t'] == 'CIRCLE' and e.get('8') == 'CLEARANCE'][0]
tx, ty, r = float(c['10']), float(c['20']), float(c['40'])
eps = 1e-9
fail = []
if dw < rules['door_clear_width_min']['min'] - eps:
    fail.append('door_clear_width_min')
rg = rules['toilet_centerline_from_side_wall_range']
if not (rg['min'] - eps <= cl <= rg['max'] + eps):
    fail.append('toilet_centerline_from_side_wall_range')
if ls < rules['side_grab_bar_length_min']['min'] - eps:
    fail.append('side_grab_bar_length_min')
if lr < rules['rear_grab_bar_length_min']['min'] - eps:
    fail.append('rear_grab_bar_length_min')
if not (min(rear[0], rear[2]) - eps <= cx <= max(rear[0], rear[2]) + eps):
    fail.append('rear_grab_bar_toilet_centerline_span')
if 2 * r < rules['turning_circle_diameter_min']['min'] - eps:
    fail.append('turning_circle_diameter_min')
fit = rules['turning_circle_fit_usable_floor']
o = fit['wall_offset']
ok = (tx - r >= xmin + o - eps and tx + r <= xmax - o + eps and
      ty - r >= ymin + o - eps and ty + r <= ymax - o + eps)
for lay in fit['blocking_layers']:
    bx0, by0, bx1, by1 = ext(segs(lay))
    dx = max(bx0 - tx, 0, tx - bx1)
    dy = max(by0 - ty, 0, ty - by1)
    if math.hypot(dx, dy) < r - eps:
        ok = False
if not ok:
    fail.append('turning_circle_fit_usable_floor')
res = {
    'room': {'xmin': round(xmin, 3), 'ymin': round(ymin, 3), 'xmax': round(xmax, 3), 'ymax': round(ymax, 3)},
    'measurements': {
        'door_clear_width': round(dw, 3),
        'toilet_centerline_from_side_wall': round(cl, 3),
        'side_grab_bar_length': round(ls, 3),
        'rear_grab_bar_length': round(lr, 3),
        'turning_circle_diameter': round(2 * r, 3),
    },
    'violations': [{'rule': k, 'element': rules[k]['element']} for k in sorted(fail)],
}
json.dump(res, open('/root/work/ada_check.json', 'w'), indent=2)
EOF
python3 /tmp/solve_ada.py
