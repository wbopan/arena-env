import csv
import json
import math
from pathlib import Path

P = Path('/root/work/timing_result.json')


def expected():
    with open('/root/work/lightcurve.csv') as f:
        photometry = [r for r in csv.DictReader(f) if int(r['quality']) == 0]
    with open('/root/work/windows.csv') as f:
        windows = list(csv.DictReader(f))
    points = []
    for window in windows:
        predicted = float(window['predicted_center_days'])
        selected = [(float(r['time_days']), max(0.0, 1-float(r['flux'])/float(r['reference']))) for r in photometry if abs(float(r['time_days'])-predicted) <= 0.16]
        center = sum(t*d for t, d in selected)/sum(d for _, d in selected)
        points.append((int(window['event_number']), center))
    count = len(points)
    mean_n = sum(n for n, _ in points)/count
    mean_t = sum(t for _, t in points)/count
    period = sum((n-mean_n)*(t-mean_t) for n, t in points)/sum((n-mean_n)**2 for n, _ in points)
    intercept = mean_t-period*mean_n
    rms = math.sqrt(sum((t-intercept-period*n)**2 for n, t in points)/count)*1440
    return {'t0_days': intercept, 'period_days': period, 'rms_oc_minutes': rms, 'event_count': count}


def actual():
    return json.loads(P.read_text())


def test_file_exists():
    assert P.is_file()


def test_schema():
    got = actual()
    assert set(got) == {'t0_days', 'period_days', 'rms_oc_minutes', 'event_count'}
    assert type(got['event_count']) is int
    assert all(type(got[k]) in (int, float) and math.isfinite(got[k]) for k in ('t0_days', 'period_days', 'rms_oc_minutes'))


def test_event_count_and_ephemeris():
    got, want = actual(), expected()
    assert got['event_count'] == want['event_count']
    assert abs(got['t0_days']-want['t0_days']) <= 0.00000051
    assert abs(got['period_days']-want['period_days']) <= 0.00000051


def test_timing_scatter():
    assert abs(actual()['rms_oc_minutes']-expected()['rms_oc_minutes']) <= 0.00051
