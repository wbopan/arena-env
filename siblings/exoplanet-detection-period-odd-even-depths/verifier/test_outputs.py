import csv
import math
from pathlib import Path

P = Path('/root/work/odd_even.csv')


def reference():
    with open('/root/work/candidates.csv') as f:
        candidates = list(csv.DictReader(f))
    with open('/root/work/photometry.csv') as f:
        observations = list(csv.DictReader(f))
    buckets = {c['id']: {0: [], 1: []} for c in candidates}
    background = []
    for r in observations:
        if int(r['quality']) != 0:
            continue
        t = float(r['time_days'])
        y = float(r['flux']) / float(r['reference'])
        w = float(r['sigma']) ** -2
        matching = []
        for c in candidates:
            p, e, d = (float(c[k]) for k in ('period_days', 'epoch_days', 'duration_days'))
            n = math.floor((t-e)/p + 0.5)
            if abs(t-e-n*p) <= d/2:
                matching.append((c['id'], n % 2))
        if not matching:
            background.append((y, w))
        elif len(matching) == 1:
            key, parity = matching[0]
            buckets[key][parity].append((y, w))
    mean = lambda pairs: sum(y*w for y, w in pairs) / sum(w for _, w in pairs)
    baseline = mean(background)
    result = []
    for c in candidates:
        a = (baseline-mean(buckets[c['id']][1]))*1e6
        b = (baseline-mean(buckets[c['id']][0]))*1e6
        delta = abs(a-b)
        result.append({'id': c['id'], 'odd_depth_ppm': a, 'even_depth_ppm': b, 'delta_ppm': delta, 'verdict': 'alternating' if delta >= 2000 else 'consistent'})
    return result


def actual():
    with P.open(newline='') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ['id', 'odd_depth_ppm', 'even_depth_ppm', 'delta_ppm', 'verdict']
        return list(reader)


def test_file_exists():
    assert P.is_file()


def test_schema_and_order():
    rows = actual()
    assert [r['id'] for r in rows] == [r['id'] for r in reference()]
    assert all(set(r) == {'id', 'odd_depth_ppm', 'even_depth_ppm', 'delta_ppm', 'verdict'} for r in rows)


def test_odd_even_depths():
    for got, want in zip(actual(), reference()):
        for field in ('odd_depth_ppm', 'even_depth_ppm'):
            assert abs(int(got[field])-want[field]) <= 0.501


def test_delta_and_verdict():
    for got, want in zip(actual(), reference()):
        assert abs(int(got['delta_ppm'])-want['delta_ppm']) <= 0.501
        assert got['verdict'] == want['verdict']
