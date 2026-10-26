import json
from pathlib import Path

import numpy as np
from scipy.signal import hilbert

ROOT = Path('/root/work')
OUT = ROOT / 'phase_peak.json'


def expected():
    data = np.load(ROOT / 'strain.npy')
    base = np.load(ROOT / 'template.npy')
    weights = np.load(ROOT / 'noise_psd.npy')
    data_f = np.fft.rfft(data)
    projections = []
    for component in (base, hilbert(base).imag):
        component_f = np.fft.rfft(component)
        correlation = np.fft.irfft(data_f * np.conj(component_f) / weights, n=len(data))
        autocorrelation = np.fft.irfft(component_f * np.conj(component_f) / weights, n=len(data))[0]
        projections.append(correlation / np.sqrt(autocorrelation))
    strength = np.hypot(*projections)
    lag = 128 + int(np.argmax(strength[128:896]))
    return lag, float(strength[lag]), float(np.arctan2(projections[1][lag], projections[0][lag]))


def result():
    return json.loads(OUT.read_text(encoding='utf-8'))


def test_exists():
    assert OUT.is_file()


def test_schema():
    obj = result()
    assert set(obj) == {'lag_samples', 'peak_snr', 'phase_rad'}
    assert type(obj['lag_samples']) is int
    assert all(type(obj[k]) in (float, int) for k in ('peak_snr', 'phase_rad'))


def test_peak_lag():
    assert result()['lag_samples'] == expected()[0]


def test_peak_snr():
    assert abs(result()['peak_snr'] - expected()[1]) <= 5.1e-7


def test_phase():
    assert abs(result()['phase_rad'] - expected()[2]) <= 5.1e-7
