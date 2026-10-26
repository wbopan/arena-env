import json
import math
import struct
import wave
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'energies.json'


def expected():
    with wave.open(str(ROOT / 'lecture_audio.wav'), 'rb') as wav:
        rate = wav.getframerate()
        assert wav.getnchannels() == 1 and wav.getsampwidth() == 2
        raw = wav.readframes(wav.getnframes())
    values = struct.unpack('<' + 'h' * (len(raw) // 2), raw)
    width = rate // 2
    chunks = [values[i:i + width] for i in range(0, len(values), width)]
    rms = [math.sqrt(sum(int(x) * int(x) for x in chunk) / len(chunk)) for chunk in chunks]
    mean = sum(rms) / len(rms)
    return rate, rms, {'min': min(rms), 'max': max(rms), 'mean': mean,
                       'std': math.sqrt(sum((x - mean) ** 2 for x in rms) / len(rms))}


def test_file_exists():
    assert OUT.is_file()


def test_schema():
    obj = json.loads(OUT.read_text())
    assert set(obj) == {'sample_rate', 'window_seconds', 'total_seconds', 'energies', 'stats'}
    assert set(obj['stats']) == {'min', 'max', 'mean', 'std'}
    assert isinstance(obj['energies'], list)


def test_window_metadata():
    obj = json.loads(OUT.read_text())
    rate, energies, _ = expected()
    assert obj['sample_rate'] == rate
    assert obj['window_seconds'] == 0.5
    assert len(obj['energies']) == len(energies)
    assert obj['total_seconds'] == len(energies) * 0.5


def test_energies_and_stats():
    obj = json.loads(OUT.read_text())
    _, energies, stats = expected()
    for actual, value in zip(obj['energies'], energies, strict=True):
        assert math.isclose(actual, round(value, 3), abs_tol=0.001)
    for key, value in stats.items():
        assert math.isclose(obj['stats'][key], round(value, 3), abs_tol=0.001)
