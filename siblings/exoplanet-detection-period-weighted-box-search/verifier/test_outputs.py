import csv
import json
import math
from pathlib import Path

P = Path('/root/work/box_result.json')


def expected():
    with open('/root/work/lightcurve.csv') as f:
        rows = [r for r in csv.DictReader(f) if int(r['quality']) == 0]
    observations = [(float(r['time_days']), float(r['flux']) / float(r['reference']), 1 / float(r['sigma']) ** 2) for r in rows]
    start = min(t for t, _, _ in observations)
    with open('/root/work/trials.csv') as f:
        trials = list(csv.DictReader(f))
    winner = None
    for trial in trials:
        period, duration = float(trial['period_days']), float(trial['duration_days'])
        for j in range(40):
            epoch = start + j * period / 40
            inside = [(y, weight) for t, y, weight in observations if abs((t - epoch + period / 2) % period - period / 2) <= duration / 2]
            outside = [(y, weight) for t, y, weight in observations if abs((t - epoch + period / 2) % period - period / 2) > duration / 2]
            wi, wo = sum(w for _, w in inside), sum(w for _, w in outside)
            if not wi or not wo:
                continue
            depth = sum(y*w for y, w in outside)/wo - sum(y*w for y, w in inside)/wi
            score = depth / math.sqrt(1/wi + 1/wo)
            if winner is None or score > winner[0]:
                winner = score, period, epoch, depth
    s, period, epoch, depth = winner
    return dict(period_days=period, epoch_days=epoch, depth_fraction=depth, snr=s)


def output():
    return json.loads(P.read_text())


def test_file_exists():
    assert P.is_file()


def test_schema():
    obj = output()
    assert set(obj) == {'period_days', 'epoch_days', 'depth_fraction', 'snr'}
    assert all(type(v) in (float, int) and math.isfinite(v) for v in obj.values())


def test_selected_trial_and_epoch():
    got, want = output(), expected()
    assert abs(got['period_days'] - want['period_days']) <= 0.0000051
    assert abs(got['epoch_days'] - want['epoch_days']) <= 0.0000051


def test_depth_and_score():
    got, want = output(), expected()
    assert abs(got['depth_fraction'] - want['depth_fraction']) <= 0.00000051
    assert abs(got['snr'] - want['snr']) <= 0.00051
