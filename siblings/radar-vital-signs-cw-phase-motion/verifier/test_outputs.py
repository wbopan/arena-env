import json
from pathlib import Path

import numpy as np

BASE = Path('/root/work')
OUT = BASE / 'motion_summary.json'


def expected():
    answer = []
    for j in range(1, 4):
        name = f'motion_{j:02d}'
        meta = json.loads((BASE / (name + '.json')).read_text())
        raw = np.fromfile(BASE / (name + '.bin'), dtype='<f4')
        assert len(raw) == 2 * meta['sample_count']
        z = raw[::2].astype(float) + 1j * raw[1::2].astype(float)
        angle = np.unwrap(np.angle(z - z.mean()))
        time = np.arange(len(z)) / meta['sample_rate_hz']
        design = np.column_stack((time, np.ones(len(time))))
        coefficients = np.linalg.lstsq(design, angle, rcond=None)[0]
        mm = (angle - design @ coefficients) * 299792458000 / (4 * np.pi * meta['carrier_frequency_hz'])
        answer.append((name, float(np.sqrt(np.mean(mm * mm))), float(np.ptp(mm))))
    return answer


def rows():
    return json.loads(OUT.read_text())


def test_file_exists():
    assert OUT.is_file()


def test_schema_and_order():
    data = rows()
    assert isinstance(data, list) and len(data) == 3
    assert [r['capture_id'] for r in data] == [f'motion_{j:02d}' for j in range(1, 4)]
    for row in data:
        assert set(row) == {'capture_id', 'rms_displacement_mm', 'peak_to_peak_mm'}
        assert isinstance(row['rms_displacement_mm'], (int, float))
        assert isinstance(row['peak_to_peak_mm'], (int, float))


def test_rms():
    for row, (_, rms, _) in zip(rows(), expected()):
        assert abs(row['rms_displacement_mm'] - rms) <= 0.00051


def test_peak_to_peak():
    for row, (_, _, extent) in zip(rows(), expected()):
        assert abs(row['peak_to_peak_mm'] - extent) <= 0.00051
