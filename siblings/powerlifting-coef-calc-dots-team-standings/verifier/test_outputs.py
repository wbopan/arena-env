import csv
import json
import os

import pytest

W = '/root/work'
OUT = os.path.join(W, 'team_standings.json')
MEN = (-0.0000010930, 0.0007391293, -0.1918759221, 24.0900756, -307.75076, 40.0, 210.0)
WOMEN = (-0.0000010706, 0.0005158568, -0.1126655495, 13.6175032, -57.96288, 40.0, 150.0)


def dots(sex, bw, total):
    a, b, c, d, e, lo, hi = WOMEN if sex == 'F' else MEN
    x = min(max(bw, lo), hi)
    return total * 500.0 / (a * x ** 4 + b * x ** 3 + c * x ** 2 + d * x + e)


def expected():
    teams = {}
    with open(os.path.join(W, 'lifters.csv'), newline='') as f:
        for r in csv.DictReader(f):
            vals = []
            for k in ('Best3SquatKg', 'Best3BenchKg', 'Best3DeadliftKg'):
                s = r[k].strip()
                vals.append(float(s) if s else 0.0)
            score = dots(r['Sex'], float(r['BodyweightKg']), sum(vals)) if min(vals) > 0 else 0.0
            teams.setdefault(r['Team'], []).append((score, r['Name']))
    res = {}
    for t, members in teams.items():
        members.sort(key=lambda z: (-z[0], z[1]))
        top = members[:3]
        res[t] = (sum(z[0] for z in top), [z[1] for z in top])
    return res


@pytest.fixture
def data():
    with open(OUT) as f:
        return json.load(f)


def test_file_exists_and_is_list():
    assert os.path.isfile(OUT)
    with open(OUT) as f:
        d = json.load(f)
    assert isinstance(d, list) and len(d) > 0


def test_schema(data):
    for o in data:
        assert set(o.keys()) == {'rank', 'team', 'score', 'top_lifters'}
        assert isinstance(o['rank'], int)
        assert isinstance(o['top_lifters'], list)


def test_teams_present(data):
    exp = expected()
    assert sorted(o['team'] for o in data) == sorted(exp)


def test_scores(data):
    exp = expected()
    for o in data:
        assert abs(float(o['score']) - exp[o['team']][0]) <= 0.011, (o['team'], o['score'], exp[o['team']][0])


def test_ranking_order(data):
    exp = expected()
    order = sorted(exp, key=lambda t: -exp[t][0])
    assert [o['team'] for o in data] == order
    assert [o['rank'] for o in data] == list(range(1, len(order) + 1))


def test_top_lifters(data):
    exp = expected()
    for o in data:
        assert o['top_lifters'] == exp[o['team']][1], o['team']
