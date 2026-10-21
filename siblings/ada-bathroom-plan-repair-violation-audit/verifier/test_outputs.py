import functools
import json
import math
from pathlib import Path

import pytest

WORK = Path('/root/work')
OUT = WORK / 'ada_check.json'
TOL = 0.01


def parse_dxf(path):
    lines = [l.strip() for l in path.read_text().splitlines()]
    pairs = list(zip(lines[0::2], lines[1::2]))
    start = pairs.index(('2', 'ENTITIES'))
    ents = []
    cur = None
    for c, v in pairs[start + 1:]:
        if c == '0':
            if cur is not None:
                ents.append(cur)
            if v == 'ENDSEC':
                break
            cur = {'type': v, 'g': {}}
        elif cur is not None:
            cur['g'].setdefault(c, []).append(v)
    return ents


def layer_of(e):
    return e['g'].get('8', [''])[0]


def lines_on(ents, layer):
    res = []
    for e in ents:
        if e['type'] == 'LINE' and layer_of(e) == layer:
            g = e['g']
            res.append((float(g['10'][0]), float(g['20'][0]), float(g['11'][0]), float(g['21'][0])))
    return res


def bbox(ls):
    xs = [v for l in ls for v in (l[0], l[2])]
    ys = [v for l in ls for v in (l[1], l[3])]
    return min(xs), min(ys), max(xs), max(ys)


@functools.lru_cache(maxsize=1)
def expected():
    ents = parse_dxf(WORK / 'ada_bath_plan.dxf')
    rules = json.loads((WORK / 'ada_rules.json').read_text())['rules']
    walls = lines_on(ents, 'WALL')
    xs = sorted({round(l[0], 4) for l in walls if abs(l[0] - l[2]) < 1e-6})
    ys = sorted({round(l[1], 4) for l in walls if abs(l[1] - l[3]) < 1e-6})
    xmin, xmax, ymin, ymax = xs[1], xs[-2], ys[1], ys[-2]
    door = [l for l in lines_on(ents, 'DOOR') if abs(l[1] - l[3]) < 1e-6][0]
    dw = abs(door[2] - door[0])
    wx0, _, wx1, _ = bbox(lines_on(ents, 'WC'))
    cx = (wx0 + wx1) / 2
    cl = min(cx - xmin, xmax - cx)
    gb = lines_on(ents, 'GRABBAR')
    side = [l for l in gb if abs(l[0] - l[2]) < 1e-6][0]
    rear = [l for l in gb if abs(l[1] - l[3]) < 1e-6][0]
    ls = abs(side[3] - side[1])
    lr = abs(rear[2] - rear[0])
    circ = [e for e in ents if e['type'] == 'CIRCLE' and layer_of(e) == 'CLEARANCE'][0]
    tcx = float(circ['g']['10'][0])
    tcy = float(circ['g']['20'][0])
    r = float(circ['g']['40'][0])
    fails = set()
    if dw < rules['door_clear_width_min']['min'] - 1e-9:
        fails.add('door_clear_width_min')
    rr = rules['toilet_centerline_from_side_wall_range']
    if cl < rr['min'] - 1e-9 or cl > rr['max'] + 1e-9:
        fails.add('toilet_centerline_from_side_wall_range')
    if ls < rules['side_grab_bar_length_min']['min'] - 1e-9:
        fails.add('side_grab_bar_length_min')
    if lr < rules['rear_grab_bar_length_min']['min'] - 1e-9:
        fails.add('rear_grab_bar_length_min')
    if not (min(rear[0], rear[2]) - 1e-9 <= cx <= max(rear[0], rear[2]) + 1e-9):
        fails.add('rear_grab_bar_toilet_centerline_span')
    if 2 * r < rules['turning_circle_diameter_min']['min'] - 1e-9:
        fails.add('turning_circle_diameter_min')
    fr = rules['turning_circle_fit_usable_floor']
    o = fr['wall_offset']
    ok = (tcx - r >= xmin + o - 1e-9 and tcx + r <= xmax - o + 1e-9 and
          tcy - r >= ymin + o - 1e-9 and tcy + r <= ymax - o + 1e-9)
    for lay in fr['blocking_layers']:
        bx0, by0, bx1, by1 = bbox(lines_on(ents, lay))
        d = math.hypot(max(bx0 - tcx, 0, tcx - bx1), max(by0 - tcy, 0, tcy - by1))
        if d < r - 1e-9:
            ok = False
    if not ok:
        fails.add('turning_circle_fit_usable_floor')
    viol = [{'rule': k, 'element': rules[k]['element']} for k in sorted(fails)]
    return {
        'room': {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax},
        'measurements': {
            'door_clear_width': dw,
            'toilet_centerline_from_side_wall': cl,
            'side_grab_bar_length': ls,
            'rear_grab_bar_length': lr,
            'turning_circle_diameter': 2 * r,
        },
        'violations': viol,
    }


def load():
    return json.loads(OUT.read_text())


def test_output_exists_and_is_json():
    assert OUT.exists()
    assert isinstance(load(), dict)


def test_schema():
    d = load()
    for k in ('room', 'measurements', 'violations'):
        assert k in d
    for k in ('xmin', 'ymin', 'xmax', 'ymax'):
        assert isinstance(d['room'][k], (int, float))
    for k in expected()['measurements']:
        assert isinstance(d['measurements'][k], (int, float))
    assert isinstance(d['violations'], list)
    for v in d['violations']:
        assert set(v.keys()) >= {'rule', 'element'}


def test_room_interior():
    d = load()
    for k, v in expected()['room'].items():
        assert d['room'][k] == pytest.approx(v, abs=TOL), k


def test_measurements():
    d = load()
    for k, v in expected()['measurements'].items():
        assert d['measurements'][k] == pytest.approx(v, abs=TOL), k


def test_violation_set():
    d = load()
    got = {(v['rule'], v['element']) for v in d['violations']}
    exp = {(v['rule'], v['element']) for v in expected()['violations']}
    assert got == exp


def test_violations_sorted_unique():
    d = load()
    names = [v['rule'] for v in d['violations']]
    assert names == sorted(names)
    assert len(names) == len(set(names))
