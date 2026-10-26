import csv
import math
from pathlib import Path
from statistics import mean, stdev
from openpyxl import load_workbook

ROOT = Path('/root/work')
OUT = ROOT / 'paired_response.csv'
HEADER = ['protein_id', 'n_pairs', 'mean_log2_delta', 'sd_log2_delta', 'geometric_fold_change']

def inputs():
    wb = load_workbook(ROOT / 'paired_expression.xlsx', data_only=True)
    data = list(wb['Data'].values)
    columns = {name: j for j, name in enumerate(data[0])}
    proteins = {row[0]: row for row in data[1:]}
    pairs = list(wb['Pairs'].values)[1:]
    targets = [row[0] for row in list(wb['Targets'].values)[1:]]
    return columns, proteins, pairs, targets

def output():
    with OUT.open(newline='') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == HEADER
        return list(reader)

def test_file_exists():
    assert OUT.is_file()

def test_schema_and_target_order():
    rows = output()
    targets = inputs()[3]
    assert [r['protein_id'] for r in rows] == targets
    assert all(set(r) == set(HEADER) and None not in r for r in rows)

def test_pair_counts():
    rows = output()
    count = len(inputs()[2])
    assert all(int(r['n_pairs']) == count for r in rows)

def test_difference_statistics():
    columns, proteins, pairs, _ = inputs()
    for row in output():
        source = proteins[row['protein_id']]
        differences = [source[columns[treated]] - source[columns[control]] for _, control, treated in pairs]
        assert math.isclose(float(row['mean_log2_delta']), mean(differences), abs_tol=0.000051)
        assert math.isclose(float(row['sd_log2_delta']), stdev(differences), abs_tol=0.000051)

def test_geometric_fold_changes():
    columns, proteins, pairs, _ = inputs()
    for row in output():
        source = proteins[row['protein_id']]
        delta = sum(source[columns[t]] - source[columns[c]] for _, c, t in pairs) / len(pairs)
        assert math.isclose(float(row['geometric_fold_change']), 2 ** delta, abs_tol=0.000051)
