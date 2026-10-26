import json
import math
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'initial_silence.json'


def expected():
    values = json.loads((ROOT / 'energies.json').read_text())['energies']
    limit = 2 * sum(values[:6]) / 6
    averages = [sum(values[max(0, k - 2):k + 1]) / min(k + 1, 3)
                for k in range(len(values))]
    choices = [k for k in range(6, len(values) - 2)
               if all(averages[j] > limit for j in range(k, k + 3))]
    return limit, (choices[0] if choices else 0)


def test_exists():
    assert OUT.is_file()


def test_schema():
    data = json.loads(OUT.read_text())
    assert set(data) == {'method', 'threshold', 'segments', 'total_segments', 'total_duration_seconds'}
    assert data['method'] == 'trailing_energy_transition'
    assert isinstance(data['segments'], list)
    assert all(set(segment) == {'start', 'end', 'duration'} for segment in data['segments'])


def test_threshold():
    limit, _ = expected()
    assert math.isclose(json.loads(OUT.read_text())['threshold'], round(limit, 3), abs_tol=0.001)


def test_opening_interval():
    _, end = expected()
    data = json.loads(OUT.read_text())
    assert data['segments'] == ([{'start': 0, 'end': end, 'duration': end}] if end else [])


def test_totals():
    data = json.loads(OUT.read_text())
    assert data['total_segments'] == len(data['segments'])
    assert data['total_duration_seconds'] == sum(s['duration'] for s in data['segments'])
