import csv
import re
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'urine_ratios.csv'
FIELDS = ['collection_id', 'uacr_mg_g', 'upcr_mg_g']

def expected():
    result = []
    with (ROOT / 'spot_urine.csv').open(newline='') as f:
        for row in csv.DictReader(f):
            if any(not row[k].strip() for k in ('albumin_value', 'protein_value', 'creatinine_value')):
                continue
            def number(k):
                return float(row[k].strip().replace(',', '.'))
            a, p, c = (number(k) for k in ('albumin_value', 'protein_value', 'creatinine_value'))
            if row['albumin_unit'] == 'mg/dL':
                a *= 10
            if row['protein_unit'] == 'mg/L':
                p /= 10
            if row['creatinine_unit'] == 'mmol/L':
                c *= 11.3
            result.append((row['collection_id'], a / (c / 100), p / c * 1000))
    return result

def output():
    with OUT.open(newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)

def test_exists():
    assert OUT.is_file()

def test_schema_and_count():
    fields, rows = output()
    assert fields == FIELDS
    assert len(rows) == len(expected())
    assert all(set(row) == set(FIELDS) and None not in row for row in rows)

def test_order_and_filter():
    _, rows = output()
    assert [r['collection_id'] for r in rows] == [r[0] for r in expected()]

def test_decimal_format():
    _, rows = output()
    assert all(re.fullmatch(r'\d+\.\d{2}', r[k]) for r in rows for k in FIELDS[1:])

def test_ratios():
    _, rows = output()
    for row, (_, uacr, upcr) in zip(rows, expected()):
        assert abs(float(row['uacr_mg_g']) - uacr) <= 0.0051
        assert abs(float(row['upcr_mg_g']) - upcr) <= 0.0051
