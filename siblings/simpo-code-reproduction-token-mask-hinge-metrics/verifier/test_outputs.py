import json
import os
import numpy as np

W = "/root/work"
OUT = os.path.join(W, "metrics.json")
TOL = 1e-5


def _expected():
    d = np.load(os.path.join(W, "tokens.npz"))
    lp = d["per_token_logps"].astype(np.float64)
    m = (d["labels"] != -100).astype(np.float64)
    avg = (lp * m).sum(1) / m.sum(1)
    B = lp.shape[0] // 2
    beta, gbr = 2.0, 0.5
    c, r = avg[:B], avg[B:]
    logits = (c - r) - gbr
    losses = np.maximum(0.0, 1.0 - beta * logits)
    cr, rr = beta * c, beta * r
    return {
        "losses": losses,
        "mean_loss": losses.mean(),
        "reward_accuracy": float((cr > rr).mean()),
        "reward_margin_mean": float((cr - rr).mean()),
        "chosen_rewards_mean": float(cr.mean()),
    }


def _load():
    with open(OUT) as f:
        return json.load(f)


def test_exists():
    assert os.path.exists(OUT)


def test_schema():
    g = _load()
    e = _expected()
    for k in e:
        assert k in g, k
    assert isinstance(g["losses"], list) and len(g["losses"]) == len(e["losses"])


def test_losses():
    g = _load()
    e = _expected()
    assert np.allclose(np.array(g["losses"], dtype=float), e["losses"], atol=TOL, rtol=0)
    assert abs(float(g["mean_loss"]) - e["mean_loss"]) < TOL


def test_reward_metrics():
    g = _load()
    e = _expected()
    for k in ["reward_accuracy", "reward_margin_mean", "chosen_rewards_mean"]:
        assert abs(float(g[k]) - e[k]) < TOL, (k, g[k], e[k])
