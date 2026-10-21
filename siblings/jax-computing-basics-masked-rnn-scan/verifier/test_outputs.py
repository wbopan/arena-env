import os
import numpy as np
import pytest

W = "/root/work"
OUT = os.path.join(W, "hseq.npy")


def expected():
    seq = np.load(os.path.join(W, "seq.npy"))
    lengths = np.load(os.path.join(W, "lengths.npy"))
    p = np.load(os.path.join(W, "rnn_params.npz"))
    Wx, Wh, b, h0 = p["Wx"], p["Wh"], p["b"], p["h0"]
    B, T, _ = seq.shape
    H = Wh.shape[0]
    res = np.zeros((B, T, H))
    for i in range(B):
        h = h0[i].copy()
        for t in range(int(lengths[i])):
            h = np.tanh(seq[i, t] @ Wx + h @ Wh + b)
            res[i, t] = h
    return res, lengths


def load_out():
    assert os.path.exists(OUT), "hseq.npy missing"
    return np.load(OUT)


def test_exists():
    assert os.path.exists(OUT)


def test_shape_dtype():
    out = load_out()
    exp, _ = expected()
    assert out.shape == exp.shape
    assert np.issubdtype(out.dtype, np.floating)


def test_padding_zero():
    out = load_out()
    _, lengths = expected()
    for i, L in enumerate(lengths):
        assert np.all(out[i, int(L):] == 0.0), f"padded steps of sequence {i} not zero"


def test_values():
    out = load_out()
    exp, _ = expected()
    assert np.allclose(out, exp, rtol=0, atol=1e-6), f"max err {np.abs(out-exp).max()}"
