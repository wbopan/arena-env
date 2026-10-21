import csv
import json
from pathlib import Path

import numpy as np
import pytest
from scipy.signal import welch

WORK = Path('/root/work')
OUT = WORK / 'range_results.csv'
IDS = [f'cap_{i:02d}' for i in range(1, 5)]


def expected(cid):
    meta = json.loads((WORK / f'{cid}.json').read_text())
    raw = np.fromfile(WORK / f'{cid}.bin', dtype='<i2').astype(np.float64) * meta['scale_factor']
    iq = raw[0::2] + 1j * raw[1::2]
    F, N = meta['n_frames'], meta['samples_per_chirp']
    R = np.fft.fft(iq.reshape(F, N), axis=1)
    R = R - R.mean(axis=0, keepdims=True)
    mag = np.abs(R).mean(axis=0)
    rpb = meta['range_per_bin_m']
    ks = [k for k in range(N) if 0.3 - 1e-9 <= k * rpb <= 1.5 + 1e-9]
    best = ks[int(np.argmax(mag[ks]))]
    ph = np.unwrap(np.angle(R[:, best]))
    ph = ph - ph.mean()
    fs = meta['frame_rate_hz']
    f, p = welch(ph, fs=fs, nperseg=F, noverlap=F // 2, nfft=16 * F, detrend='constant')
    m = (f >= 0.08) & (f <= 0.5)
    br = f[m][int(np.argmax(p[m]))] * 60.0
    return best, best * rpb, br


@pytest.fixture(scope='module')
def rows():
    assert OUT.exists(), 'range_results.csv not found'
    with open(OUT) as fh:
        rd = csv.DictReader(fh)
        assert [c.strip() for c in rd.fieldnames] == ['capture_id', 'range_bin', 'range_m', 'breathing_rate_bpm']
        return {r['capture_id'].strip(): r for r in rd}


def test_file_exists():
    assert OUT.exists()


def test_all_ids(rows):
    assert sorted(rows.keys()) == IDS


def test_range_bin(rows):
    for cid in IDS:
        b, _, _ = expected(cid)
        assert int(float(rows[cid]['range_bin'])) == b, f'{cid}: expected bin {b}, got {rows[cid]["range_bin"]}'


def test_range_m(rows):
    for cid in IDS:
        _, r, _ = expected(cid)
        assert abs(float(rows[cid]['range_m']) - r) <= 0.006, f'{cid}: expected {r:.2f} m'


def test_breathing_rate(rows):
    for cid in IDS:
        _, _, br = expected(cid)
        got = float(rows[cid]['breathing_rate_bpm'])
        assert abs(got - br) <= 1.0, f'{cid}: expected ~{br:.1f} bpm, got {got}'
