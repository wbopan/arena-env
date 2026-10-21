import json
import os

import pytest

WORK = '/root/work'
OUT = os.path.join(WORK, 'waterfall_report.json')


def expected():
    with open(os.path.join(WORK, 'api_routes.json')) as f:
        data = json.load(f)
    res = []
    for r in data['routes']:
        dur = {o['name']: o['duration_ms'] for o in r['operations']}
        deps = {o['name']: list(o['depends_on']) for o in r['operations']}
        ef = {}

        def finish(n):
            if n not in ef:
                ef[n] = dur[n] + max((finish(d) for d in deps[n]), default=0)
            return ef[n]

        for n in dur:
            finish(n)
        opt = max(ef.values())
        seq = sum(dur.values())
        cur = sorted(n for n in ef if ef[n] == opt)[0]
        path = [cur]
        while deps[cur]:
            best = max(ef[d] for d in deps[cur])
            cur = sorted(d for d in deps[cur] if ef[d] == best)[0]
            path.append(cur)
        path.reverse()
        res.append({'route': r['route'], 'sequential_ms': seq, 'optimal_ms': opt,
                    'saved_ms': seq - opt, 'speedup': round(seq / opt, 3),
                    'critical_path': path})
    return res


@pytest.fixture(scope='module')
def report():
    assert os.path.isfile(OUT), 'waterfall_report.json missing'
    with open(OUT) as f:
        return json.load(f)


@pytest.fixture(scope='module')
def exp():
    return expected()


def test_output_exists():
    assert os.path.isfile(OUT)


def test_schema(report, exp):
    assert isinstance(report.get('routes'), list)
    assert 'total_saved_ms' in report
    assert len(report['routes']) == len(exp)
    for got, e in zip(report['routes'], exp):
        for key in ['route', 'sequential_ms', 'optimal_ms', 'saved_ms', 'speedup', 'critical_path']:
            assert key in got, f'missing {key}'
        assert got['route'] == e['route'], 'route order differs from input'


def test_times(report, exp):
    for got, e in zip(report['routes'], exp):
        assert int(got['sequential_ms']) == e['sequential_ms'], e['route']
        assert int(got['optimal_ms']) == e['optimal_ms'], e['route']
        assert int(got['saved_ms']) == e['saved_ms'], e['route']


def test_speedup(report, exp):
    for got, e in zip(report['routes'], exp):
        assert abs(float(got['speedup']) - e['speedup']) <= 0.0011, e['route']


def test_critical_path(report, exp):
    for got, e in zip(report['routes'], exp):
        assert list(got['critical_path']) == e['critical_path'], e['route']


def test_total_saved(report, exp):
    assert int(report['total_saved_ms']) == sum(e['saved_ms'] for e in exp)
