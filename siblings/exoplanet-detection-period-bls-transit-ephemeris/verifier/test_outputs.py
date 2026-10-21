import functools
import json
import os

import numpy as np
import pytest

INP = '/root/work/tess_lc.txt'
OUT = '/root/work/transit.json'


@functools.lru_cache(maxsize=1)
def reference():
    d = np.loadtxt(INP, comments='#')
    d = d[d[:, 2] == 0]
    d = d[np.argsort(d[:, 0])]
    t = d[:, 0]
    f = d[:, 1]
    t_first = float(t[0])
    trend = np.array([np.median(f[np.abs(t - ti) <= 0.5]) for ti in t])
    y = f / trend
    r = y - np.median(y)
    sig = 1.4826 * np.median(np.abs(r))
    keep = r < 5 * sig
    t = t[keep]
    y = y[keep]
    dy = y - y.mean()
    n = len(y)
    nb = 200
    durs = [0.07, 0.1, 0.13, 0.16, 0.19]
    best = (-np.inf, None, None)
    for P in np.arange(1.0, 5.0, 0.0005):
        idx = np.minimum((((t - t[0]) / P) % 1.0 * nb).astype(int), nb - 1)
        s = np.bincount(idx, weights=dy, minlength=nb)
        c = np.bincount(idx, minlength=nb).astype(float)
        cs = np.concatenate([[0.0], np.cumsum(np.concatenate([s, s]))])
        cc = np.concatenate([[0.0], np.cumsum(np.concatenate([c, c]))])
        for dur in durs:
            k = max(1, int(round(dur / P * nb)))
            S = cs[k:k + nb] - cs[:nb]
            R = (cc[k:k + nb] - cc[:nb]) / n
            ok = (R > 0) & (R < 1) & (S < 0)
            if not ok.any():
                continue
            m = np.max(S[ok] ** 2 / (R[ok] * (1 - R[ok])))
            if m > best[0]:
                best = (m, P, dur)
    _, P, dur = best
    b0 = (-np.inf, None, None)
    for t0 in t_first + np.arange(0.0, P, 0.002):
        ph = (t - t0 + 0.5 * P) % P - 0.5 * P
        msk = np.abs(ph) < 0.5 * dur
        if msk.sum() == 0 or msk.all():
            continue
        S = dy[msk].sum()
        if S >= 0:
            continue
        R = msk.mean()
        sc = S ** 2 / (R * (1 - R))
        if sc > b0[0]:
            b0 = (sc, t0, msk)
    _, t0, msk = b0
    depth = (y[~msk].mean() - y[msk].mean()) * 1000.0
    return float(P), float(t0), float(depth), t_first


def load():
    with open(OUT) as fh:
        return json.load(fh)


def test_file_exists():
    assert os.path.exists(OUT), 'transit.json not found'


def test_schema():
    if not os.path.exists(OUT):
        pytest.skip('missing')
    o = load()
    assert isinstance(o, dict)
    for k in ('period_days', 't0', 'depth_ppt'):
        assert k in o, k
        float(o[k])


def test_period():
    if not os.path.exists(OUT):
        pytest.skip('missing')
    P = reference()[0]
    got = float(load()['period_days'])
    assert abs(got - P) < 0.005, (got, P)


def test_t0():
    if not os.path.exists(OUT):
        pytest.skip('missing')
    P, t0, _, t_first = reference()
    got = float(load()['t0'])
    assert t_first - 0.05 <= got <= t_first + P + 0.05, (got, t_first)
    diff = got - t0
    assert min(abs(diff), abs(diff - P), abs(diff + P)) < 0.03, (got, t0)


def test_depth():
    if not os.path.exists(OUT):
        pytest.skip('missing')
    dep = reference()[2]
    got = float(load()['depth_ppt'])
    assert abs(got - dep) <= 0.3 * dep, (got, dep)
