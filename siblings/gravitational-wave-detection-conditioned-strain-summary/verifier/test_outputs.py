import json
from pathlib import Path

import numpy as np
from scipy import signal

ROOT = Path('/root/work')
OUT = ROOT / 'conditioned_summary.json'


def expected():
    raw = np.load(ROOT / 'raw_strain.npy')
    sections = signal.butter(4, 35, btype='highpass', fs=1024, output='sos')
    filtered = signal.sosfiltfilt(sections, raw)
    cropped = signal.resample_poly(filtered, 1, 2)[64:-64]
    blocks = np.split(cropped, 4)
    return cropped, [float(np.sqrt(np.mean(b ** 2))) for b in blocks]


def result():
    return json.loads(OUT.read_text(encoding='utf-8'))


def test_file_exists():
    assert OUT.is_file()


def test_schema():
    obj = result()
    assert set(obj) == {'sample_rate_hz', 'samples', 'block_rms', 'peak_index', 'peak_abs'}
    assert isinstance(obj['block_rms'], list) and len(obj['block_rms']) == 4
    assert all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in obj['block_rms'])


def test_dimensions():
    cropped, _ = expected()
    obj = result()
    assert len(cropped) == 896
    assert obj['sample_rate_hz'] == 512
    assert obj['samples'] == len(cropped)


def test_block_rms():
    _, rms = expected()
    assert np.allclose(result()['block_rms'], rms, rtol=0, atol=5.1e-7)


def test_peak():
    cropped, _ = expected()
    obj = result()
    index = int(np.argmax(np.abs(cropped)))
    assert type(obj['peak_index']) is int and obj['peak_index'] == index
    assert abs(obj['peak_abs'] - abs(cropped[index])) <= 5.1e-7
