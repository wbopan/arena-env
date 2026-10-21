import json
from pathlib import Path

import pytest

W = Path('/root/work')
OUT = W / 'oscillation_report.json'


def compute_expected():
    raw = json.loads((W / 'preferences.json').read_text())
    pref = {int(k): v for k, v in raw.items()}

    def nxt(a):
        v = pref.get(a)
        return v if (v is not None and v in pref) else None

    n = len(pref)
    members = set()
    for a in pref:
        cur = nxt(a)
        steps = 0
        while cur is not None and steps <= n:
            if cur == a:
                members.add(a)
                break
            cur = nxt(cur)
            steps += 1
    cycles = []
    done = set()
    for a in sorted(members):
        if a in done:
            continue
        c = [a]
        cur = nxt(a)
        while cur != a:
            c.append(cur)
            cur = nxt(cur)
        done.update(c)
        cycles.append(c)
    affected = set()
    for a in pref:
        cur = a
        steps = 0
        while cur is not None and steps <= n:
            if cur in members:
                affected.add(a)
                break
            cur = nxt(cur)
            steps += 1
    return {
        'oscillation_detected': len(cycles) > 0,
        'cycles': cycles,
        'oscillating_ases': sorted(members),
        'affected_ases': sorted(affected),
        'stable_ases': sorted(set(pref) - affected),
    }


@pytest.fixture(scope='module')
def out():
    assert OUT.exists(), 'output file missing'
    return json.loads(OUT.read_text())


@pytest.fixture(scope='module')
def exp():
    return compute_expected()


def test_schema(out):
    for k in ['oscillation_detected', 'cycles', 'oscillating_ases', 'affected_ases', 'stable_ases']:
        assert k in out, k
    assert isinstance(out['cycles'], list)


def test_detected(out, exp):
    assert out['oscillation_detected'] is exp['oscillation_detected']


def test_cycles(out, exp):
    got = [[int(x) for x in c] for c in out['cycles']]
    assert got == exp['cycles']


def test_oscillating(out, exp):
    assert [int(x) for x in out['oscillating_ases']] == exp['oscillating_ases']


def test_affected_and_stable(out, exp):
    assert [int(x) for x in out['affected_ases']] == exp['affected_ases']
    assert [int(x) for x in out['stable_ases']] == exp['stable_ases']
