import csv
import math
from pathlib import Path

import yaml

ROOT = Path('/root/work')
OUT = ROOT / 'best_coincidence.yaml'


def rows(name):
    with (ROOT / name).open(newline='') as f:
        return list(csv.DictReader(f))


def expected():
    candidates = []
    for h in rows('hanford_triggers.csv'):
        for l in rows('livingston_triggers.csv'):
            ht, lt = float(h['time_s']), float(l['time_s'])
            hm, lm = float(h['total_mass_solar']), float(l['total_mass_solar'])
            if abs(lt - ht) <= 0.012 and abs(lm - hm) <= 2.0:
                power = float(h['snr']) ** 2 + float(l['snr']) ** 2
                candidates.append((-power, h['trigger_id'], l['trigger_id'], lt - ht, (hm + lm) / 2))
    best = min(candidates)
    return best[1], best[2], math.sqrt(-best[0]), best[3] * 1000, best[4]


def result():
    return yaml.safe_load(OUT.read_text(encoding='utf-8'))


def test_file_exists():
    assert OUT.is_file()


def test_mapping_schema():
    obj = result()
    assert isinstance(obj, dict)
    assert set(obj) == {'hanford_id', 'livingston_id', 'network_snr', 'delay_ms', 'mean_total_mass_solar'}
    assert type(obj['hanford_id']) is str and type(obj['livingston_id']) is str
    assert all(type(obj[k]) in (int, float) for k in ('network_snr', 'delay_ms', 'mean_total_mass_solar'))


def test_selected_pair():
    h, l, _, _, _ = expected()
    assert (result()['hanford_id'], result()['livingston_id']) == (h, l)


def test_network_snr():
    assert abs(result()['network_snr'] - expected()[2]) <= 0.00051


def test_delay_and_mass():
    obj = result()
    _, _, _, delay, mass = expected()
    assert abs(obj['delay_ms'] - delay) <= 0.00051
    assert abs(obj['mean_total_mass_solar'] - mass) <= 0.00051
