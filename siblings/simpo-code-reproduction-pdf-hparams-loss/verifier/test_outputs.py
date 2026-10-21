import os
import re
import numpy as np
from pypdf import PdfReader

W = "/root/work"
OUT = os.path.join(W, "loss.npz")


def _hp():
    text = "\n".join((p.extract_text() or "") for p in PdfReader(os.path.join(W, "paper.pdf")).pages)

    def g(k):
        m = re.search(k + r"\s*=\s*([0-9]*\.?[0-9]+)", text)
        assert m, k
        return float(m.group(1))

    return g("beta"), g("gamma"), g("label_smoothing")


def _expected():
    d = np.load(os.path.join(W, "batch.npz"))
    beta, gamma, ls = _hp()
    cr = beta * d["chosen_logps_sum"].astype(np.float64) / d["chosen_len"].astype(np.float64)
    rr = beta * d["rejected_logps_sum"].astype(np.float64) / d["rejected_len"].astype(np.float64)
    z = cr - rr - gamma
    loss = (1 - ls) * np.logaddexp(0.0, -z) + ls * np.logaddexp(0.0, z)
    return loss, cr, rr


def _load():
    return np.load(OUT)


def test_exists():
    assert os.path.exists(OUT)


def test_schema():
    g = _load()
    loss, _, _ = _expected()
    for k in ["losses", "chosen_rewards", "rejected_rewards"]:
        assert k in g.files, k
        assert np.asarray(g[k]).shape == loss.shape, k
        assert np.isfinite(np.asarray(g[k], dtype=np.float64)).all(), k


def test_rewards():
    g = _load()
    _, cr, rr = _expected()
    assert np.allclose(g["chosen_rewards"], cr, rtol=1e-5, atol=1e-6)
    assert np.allclose(g["rejected_rewards"], rr, rtol=1e-5, atol=1e-6)


def test_losses():
    g = _load()
    loss, _, _ = _expected()
    assert np.allclose(g["losses"], loss, rtol=1e-5, atol=1e-6), np.max(np.abs(g["losses"] - loss))
