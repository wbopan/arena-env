import itertools
import json
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'minimized.json'


def inputs():
    return (ROOT / 'crash.bin').read_bytes(), json.loads((ROOT / 'crash_rule.json').read_text())


def valid(data, rule):
    return len(data) >= 4 and data[:2] == bytes.fromhex(rule['magic_hex']) and 0 in data[2:] and sum(data) % 11 == rule['remainder']


def best():
    original, rule = inputs()
    for size in range(4, len(original) + 1):
        choices = []
        for indices in itertools.combinations(range(len(original)), size):
            candidate = bytes(original[i] for i in indices)
            if valid(candidate, rule):
                choices.append((candidate, indices))
        if choices:
            return min(choices)
    raise AssertionError('generator did not make a crash')


def result():
    return json.loads(OUT.read_text(encoding='utf-8'))


def test_file_exists():
    assert OUT.is_file()


def test_schema():
    obj = result()
    assert set(obj) == {'minimized_hex', 'length', 'retained_indices'}
    assert isinstance(obj['minimized_hex'], str) and isinstance(obj['length'], int)
    assert isinstance(obj['retained_indices'], list) and all(type(i) is int for i in obj['retained_indices'])


def test_is_reproducing_subsequence():
    obj = result()
    original, rule = inputs()
    indices = obj['retained_indices']
    assert indices == sorted(set(indices)) and all(0 <= i < len(original) for i in indices)
    candidate = bytes.fromhex(obj['minimized_hex'])
    assert candidate == bytes(original[i] for i in indices)
    assert obj['length'] == len(candidate) and valid(candidate, rule)


def test_global_minimum_and_ties():
    obj = result()
    data, indices = best()
    assert obj['minimized_hex'] == data.hex()
    assert obj['retained_indices'] == list(indices)
