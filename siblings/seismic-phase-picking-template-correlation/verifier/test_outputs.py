import csv
from pathlib import Path
import numpy as np

ROOT = Path('/root/work')
OUT = ROOT / 'picks.csv'


def expected():
    with np.load(ROOT / 'templates.npz') as t:
        names = str(t['channels']).split(',')
        templates = {'P': t['p_template'], 'S': t['s_template']}
        dt = float(t['dt'])
    result = {}
    for path in sorted(ROOT.glob('record_*.npz')):
        with np.load(path) as f:
            assert float(f['dt']) == dt
            recorded = str(f['channels']).split(',')
            data = f['data'][:, [recorded.index(c) for c in names]]
        for phase, template in templates.items():
            flat = template.reshape(-1)
            norm = np.linalg.norm(flat)
            scores = []
            for start in range(len(data) - len(template) + 1):
                window = data[start:start + len(template)].reshape(-1)
                scores.append(float(np.dot(flat, window) / (norm * np.linalg.norm(window))))
            best = max(range(len(scores)), key=lambda j: scores[j])
            result[(path.name, phase)] = (best, round(scores[best], 4))
    return result


def rows():
    with OUT.open(newline='') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        values = list(reader)
    return fields, values


def test_file_exists():
    assert OUT.is_file()


def test_schema_and_order():
    fields, values = rows()
    assert fields == ['file_name', 'phase', 'pick_idx', 'score']
    assert [(r['file_name'], r['phase']) for r in values] == sorted(expected(), key=lambda k: (k[0], {'P': 0, 'S': 1}[k[1]]))


def test_indices():
    _, values = rows()
    reference = expected()
    for r in values:
        assert int(r['pick_idx']) == reference[(r['file_name'], r['phase'])][0]


def test_scores():
    _, values = rows()
    reference = expected()
    for r in values:
        assert abs(float(r['score']) - reference[(r['file_name'], r['phase'])][1]) <= 0.00005
