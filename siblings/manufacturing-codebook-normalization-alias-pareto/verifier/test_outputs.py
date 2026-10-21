import csv
import json
import os
from collections import Counter

import pytest

W = '/root/work'
OUT = os.path.join(W, 'pareto.json')


def norm(s):
    s = s.lower()
    for ch in '-_.':
        s = s.replace(ch, ' ')
    return ' '.join(s.split())


def lev(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def read(name):
    with open(os.path.join(W, name), encoding='utf-8') as f:
        return list(csv.DictReader(f))


def compute_expected():
    logs = read('logs.csv')
    aliases = read('alias_table.csv')
    cb = {(r['product_id'], r['code']): r for r in read('codebook.csv')}
    counts = {}
    unknown = 0
    for r in logs:
        t = norm(r['reason_text'])
        cands = sorted((lev(t, norm(a['alias'])), a['code']) for a in aliases if a['product_id'] == r['product_id'])
        code = 'UNKNOWN'
        if cands and cands[0][0] <= 2:
            code = cands[0][1]
            scope = [x for x in cb[(r['product_id'], code)]['station_scope'].split('|') if x]
            if scope and r['station'] not in scope:
                code = 'UNKNOWN'
        if code == 'UNKNOWN':
            unknown += 1
        counts.setdefault(r['product_id'], Counter())[code] += 1
    products = {}
    for pid, c in counts.items():
        n = sum(c.values())
        items = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))
        products[pid] = [{'code': k, 'label': '' if k == 'UNKNOWN' else cb[(pid, k)]['standard_label'], 'count': v, 'share': round(v / n, 4)} for k, v in items]
    return {'total_records': len(logs), 'unknown_records': unknown, 'products': products}


def load():
    with open(OUT, encoding='utf-8') as f:
        return json.load(f)


def test_file_exists_and_parses():
    assert os.path.exists(OUT)
    d = load()
    assert isinstance(d, dict)
    for k in ('total_records', 'unknown_records', 'products'):
        assert k in d


def test_totals():
    d = load()
    e = compute_expected()
    assert int(d['total_records']) == e['total_records']
    assert int(d['unknown_records']) == e['unknown_records']


def test_product_keys():
    d = load()
    e = compute_expected()
    assert set(d['products'].keys()) == set(e['products'].keys())


def test_code_counts_and_order():
    d = load()
    e = compute_expected()
    for pid, items in e['products'].items():
        got = [(x['code'], int(x['count'])) for x in d['products'][pid]]
        assert got == [(x['code'], x['count']) for x in items], pid


def test_labels_and_shares():
    d = load()
    e = compute_expected()
    for pid, items in e['products'].items():
        got = d['products'][pid]
        assert len(got) == len(items)
        for g, x in zip(got, items):
            assert g['label'] == x['label'], (pid, x['code'])
            assert float(g['share']) == pytest.approx(x['share'], abs=1.01e-4), (pid, x['code'])
