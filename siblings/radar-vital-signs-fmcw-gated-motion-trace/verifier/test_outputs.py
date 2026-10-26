import csv
import json
from pathlib import Path

import numpy as np

BASE = Path('/root/work')
OUT = BASE / 'gated_motion.csv'
HEADER = ['capture_id', 'second', 'displacement_mm']


def reference():
    result = []
    for j in (1, 2):
        name = f'sweep_{j:02d}'
        meta = json.loads((BASE / (name + '.json')).read_text())
        samples = np.fromfile(BASE / (name + '.bin'), dtype='<i2')
        assert samples.size == meta['chirp_count'] * meta['samples_per_chirp']
        chirps = samples.astype(float).reshape(meta['chirp_count'], meta['samples_per_chirp'])
        spectrum = np.fft.rfft(chirps - chirps.mean(axis=1, keepdims=True), axis=1)
        moving = spectrum - spectrum.mean(axis=0, keepdims=True)
        allowed = [k for k in range(moving.shape[1]) if 0.3 - 1e-9 <= k * meta['range_per_bin_m'] <= 0.9 + 1e-9]
        selected = max(allowed, key=lambda k: (np.abs(moving[:, k]).mean(), -k))
        phase = np.unwrap(np.angle(moving[:, selected]))
        time = np.arange(meta['chirp_count']) / meta['chirp_rate_hz']
        design = np.column_stack((time, np.ones(len(time))))
        residual = phase - design @ np.linalg.lstsq(design, phase, rcond=None)[0]
        displacement = residual * 299792458000 / (4 * np.pi * meta['carrier_frequency_hz'])
        for index in range(0, meta['chirp_count'], meta['chirp_rate_hz']):
            result.append((name, index // meta['chirp_rate_hz'], float(displacement[index])))
    return result


def rows():
    with OUT.open(newline='') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == HEADER
        return list(reader)


def test_file_exists():
    assert OUT.is_file()


def test_schema_and_sampling_grid():
    found = rows()
    expected = reference()
    assert len(found) == len(expected) == 64
    assert [(r['capture_id'], int(r['second'])) for r in found] == [(name, sec) for name, sec, _ in expected]
    assert all(set(r) == set(HEADER) for r in found)


def test_first_capture_displacements():
    for row, (_, _, value) in zip(rows()[:32], reference()[:32]):
        assert abs(float(row['displacement_mm']) - value) <= 0.00051


def test_second_capture_displacements():
    for row, (_, _, value) in zip(rows()[32:], reference()[32:]):
        assert abs(float(row['displacement_mm']) - value) <= 0.00051
