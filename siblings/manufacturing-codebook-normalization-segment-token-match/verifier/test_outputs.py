import csv
import os
import re

import pytest

W = '/root/work'
OUT = os.path.join(W, 'segments.csv')
COLS = ['segment_id', 'record_id', 'span_text', 'pred_code', 'pred_label', 'score']


def tokens(s):
    return set(re.findall('[a-z0-9]+', s.lower()))


def compute_expected():
    with open(os.path.join(W, 'codebook.csv'), encoding='utf-8') as f:
        cb = list(csv.DictReader(f))
    with open(os.path.join(W, 'logs.csv'), encoding='utf-8') as f:
        logs = list(csv.DictReader(f))
    exp = []
    for r in logs:
        segs = [p.strip() for p in re.split('[/;+,]', r['raw_reason_text']) if p.strip()]
        for i, seg in enumerate(segs, 1):
            T = tokens(seg)
            cands = []
            for c in cb:
                if c['product_id'] != r['product_id']:
                    continue
                scope = [x for x in c['station_scope'].split('|') if x]
                if scope and r['station'] not in scope:
                    continue
                K = tokens(c['standard_label'])
                for kw in c['keywords'].split('|'):
                    K = K | tokens(kw)
                sc = (len(T & K) / len(T)) if T else 0.0
                cands.append((-sc, c['code'], c['standard_label']))
            cands.sort()
            if not cands:
                exp.append((r['record_id'] + '-S' + str(i), r['record_id'], seg, 'UNKNOWN', '', 0.0))
                continue
            nsc, code, label = cands[0]
            sc = -nsc
            if sc < 0.5:
                code, label = 'UNKNOWN', ''
            exp.append((r['record_id'] + '-S' + str(i), r['record_id'], seg, code, label, sc))
    return exp


def load_out():
    with open(OUT, encoding='utf-8', newline='') as f:
        rd = csv.reader(f)
        rows = list(rd)
    return rows[0], rows[1:]


def test_file_exists():
    assert os.path.exists(OUT), 'segments.csv missing'


def test_header():
    header, _ = load_out()
    assert [h.strip() for h in header] == COLS


def test_segment_ids_and_spans():
    _, rows = load_out()
    exp = compute_expected()
    assert [r[0] for r in rows] == [e[0] for e in exp]
    for r, e in zip(rows, exp):
        assert r[1] == e[1], r[0]
        assert r[2].strip() == e[2], r[0]


def test_pred_codes():
    _, rows = load_out()
    exp = compute_expected()
    assert len(rows) == len(exp)
    bad = [(r[0], r[3], e[3]) for r, e in zip(rows, exp) if r[3] != e[3]]
    assert not bad, 'code mismatches: %s' % bad[:5]


def test_labels_and_scores():
    _, rows = load_out()
    exp = compute_expected()
    assert len(rows) == len(exp)
    for r, e in zip(rows, exp):
        assert r[4] == e[4], r[0]
        assert float(r[5]) == pytest.approx(e[5], abs=1.01e-4), r[0]
