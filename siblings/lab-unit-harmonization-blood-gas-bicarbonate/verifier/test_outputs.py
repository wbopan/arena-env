import csv
import json
import re
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'gas_results.json'
KEYS = {'sample_id', 'pco2_mmHg', 'po2_mmHg', 'bicarbonate_mEq_L'}

def expected():
    result = []
    with (ROOT / 'arterial_gases.csv').open(newline='') as f:
        for r in csv.DictReader(f):
            def read(k):
                return float(r[k].strip().replace(',', '.'))
            co2 = read('pco2_value') * (7.5 if r['pco2_unit'] == 'kPa' else 1)
            o2 = read('po2_value') * (7.5 if r['po2_unit'] == 'kPa' else 1)
            hco3 = .03 * co2 * 10 ** (read('ph') - 6.1)
            result.append((r['sample_id'], co2, o2, hco3))
    return result

def output():
    return json.loads(OUT.read_text())

def test_exists():
    assert OUT.is_file()

def test_array_schema():
    data = output()
    assert isinstance(data, list) and len(data) == len(expected())
    assert all(isinstance(r, dict) and set(r) == KEYS for r in data)

def test_order_and_numeric_format():
    data = output()
    assert [r['sample_id'] for r in data] == [r[0] for r in expected()]
    assert all(isinstance(r[k], str) and re.fullmatch(r'\d+\.\d{2}', r[k]) for r in data for k in KEYS - {'sample_id'})

def test_pressures():
    for row, (_, co2, o2, _) in zip(output(), expected()):
        assert abs(float(row['pco2_mmHg']) - co2) <= .0051
        assert abs(float(row['po2_mmHg']) - o2) <= .0051

def test_bicarbonate():
    for row, (_, _, _, hco3) in zip(output(), expected()):
        assert abs(float(row['bicarbonate_mEq_L']) - hco3) <= .0051
