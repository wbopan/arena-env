import csv
import json
from pathlib import Path

import numpy as np

BASE = Path('/root/work')
OUT = BASE / 'cardiac_rates.csv'
HEADER = ['capture_id', 'dominant_hr_hz', 'heart_rate_bpm']


def expected():
    result = []
    for j in range(1, 4):
        name = f'pulse_{j:02d}'
        meta = json.loads((BASE / (name + '.json')).read_text())
        raw = np.fromfile(BASE / (name + '.bin'), dtype='<i2')
        assert raw.size == 2 * meta['sample_count']
        z = raw[::2].astype(float) + 1j * raw[1::2].astype(float)
        phase = np.unwrap(np.angle(z - z.mean()))
        time = np.arange(len(z)) / meta['sample_rate_hz']
        matrix = np.column_stack([time, np.ones(len(time))])
        phase -= matrix @ np.linalg.lstsq(matrix, phase, rcond=None)[0]
        frequencies = np.fft.rfftfreq(len(phase), 1 / meta['sample_rate_hz'])
        powers = np.abs(np.fft.rfft(phase)) ** 2
        candidates = np.flatnonzero((frequencies >= 0.7) & (frequencies <= 3.0))
        top = candidates[np.argmax(powers[candidates])]
        dominant = frequencies[top]
        chosen = dominant
        if 0.7 <= dominant / 2 <= 3.0 and np.interp(dominant / 2, frequencies, powers) > 0.5 * powers[top]:
            chosen = dominant / 2
        result.append((name, float(dominant), float(chosen * 60)))
    return result


def read_rows():
    with OUT.open(newline='') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == HEADER
        return list(reader)


def test_file_exists():
    assert OUT.is_file()


def test_columns_and_capture_order():
    rows = read_rows()
    assert len(rows) == 3
    assert [r['capture_id'] for r in rows] == [f'pulse_{j:02d}' for j in range(1, 4)]
    assert all(set(r) == set(HEADER) for r in rows)


def test_dominant_spectral_bins():
    for row, (_, dominant, _) in zip(read_rows(), expected()):
        assert abs(float(row['dominant_hr_hz']) - dominant) <= 0.000051


def test_harmonic_aware_heart_rates():
    for row, (_, _, bpm) in zip(read_rows(), expected()):
        assert abs(float(row['heart_rate_bpm']) - bpm) <= 0.051
