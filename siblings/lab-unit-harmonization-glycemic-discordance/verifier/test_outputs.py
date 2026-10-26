import csv
import re
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'glycemic_comparison.csv'
FIELDS = ['patient_id', 'hba1c_percent', 'eag_mg_dL', 'glucose_mg_dL', 'gap_mg_dL']

def expected():
    rows = []
    with (ROOT / 'glycemic_pairs.csv').open(newline='') as f:
        for r in csv.DictReader(f):
            h = float(r['hba1c_value'].strip().replace(',', '.'))
            g = float(r['glucose_value'].strip().replace(',', '.'))
            if r['hba1c_unit'] == 'IFCC_mmol_mol':
                h = h / 10.929 + 2.15
            if r['glucose_unit'] == 'mmol/L':
                g *= 18.02
            eag = 28.7 * h - 46.7
            rows.append((r['patient_id'], h, eag, g, g - eag))
    return rows

def output():
    with OUT.open(newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)

def test_exists():
    assert OUT.is_file()

def test_schema_and_order():
    fields, rows = output()
    assert fields == FIELDS
    assert len(rows) == len(expected())
    assert [r['patient_id'] for r in rows] == [r[0] for r in expected()]
    assert all(set(r) == set(FIELDS) and None not in r for r in rows)

def test_numeric_format():
    _, rows = output()
    assert all(re.fullmatch(r'-?\d+\.\d{2}', r[k]) for r in rows for k in FIELDS[1:])

def test_hba1c_and_eag():
    _, rows = output()
    for row, (_, h, eag, _, _) in zip(rows, expected()):
        assert abs(float(row['hba1c_percent']) - h) <= .0051
        assert abs(float(row['eag_mg_dL']) - eag) <= .0051

def test_glucose_and_gap():
    _, rows = output()
    for row, (_, _, _, glucose, gap) in zip(rows, expected()):
        assert abs(float(row['glucose_mg_dL']) - glucose) <= .0051
        assert abs(float(row['gap_mg_dL']) - gap) <= .0051
