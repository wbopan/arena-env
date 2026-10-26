import csv
from pathlib import Path

BASE = Path('/root/work')

def expected():
    with (BASE / 'stations.csv').open() as f:
        response = {r['station_id']: float(r['response']) for r in csv.DictReader(f)}
    traces = {}
    with (BASE / 'waveforms.csv').open() as f:
        for r in csv.DictReader(f):
            key = (r['station_id'], r['channel'])
            traces.setdefault(key, []).append((int(r['sample']), abs(float(r['counts'])) / response[r['station_id']]))
    result = []
    for (sid, channel), trace in traces.items():
        trace.sort()
        run = []
        def emit():
            if len(run) >= 2:
                result.append((sid, 'p' if channel == 'Z' else 's', run[0][0], max(v for _, v in run)))
        for sample, value in trace:
            if value >= 3:
                if run and sample != run[-1][0] + 1:
                    emit()
                    run = []
                run.append((sample, value))
            else:
                emit()
                run = []
        emit()
    return sorted(result, key=lambda r: (r[2], r[0], r[1]))

def actual():
    with (BASE / 'picks.csv').open() as f:
        return list(csv.DictReader(f))

def test_file_exists():
    assert (BASE / 'picks.csv').is_file()

def test_schema():
    with (BASE / 'picks.csv').open() as f:
        assert next(csv.reader(f)) == ['station_id', 'phase', 'time_s', 'peak_unit']

def test_pick_identity_and_order():
    assert [(r['station_id'], r['phase'], int(r['time_s'])) for r in actual()] == [(s, p, t) for s, p, t, _ in expected()]

def test_peak_amplitudes():
    rows = actual()
    assert len(rows) == len(expected())
    for row, (_, _, _, peak) in zip(rows, expected()):
        assert abs(float(row['peak_unit']) - peak) <= 0.00501
