import json
import os
import numpy as np
import pytest

W = "/root/work"
OUT = os.path.join(W, "result.json")
KEYS = {"loss_init", "grad_init", "w_final", "loss_final", "train_accuracy"}


def ref():
    d = np.load(os.path.join(W, "data.npz"))
    X, y, w = d["X"], d["y"], d["w0"].copy()
    cfg = json.load(open(os.path.join(W, "config.json")))
    lam = cfg["l2"]

    def loss(w):
        m = y * (X @ w)
        return float(np.mean(np.logaddexp(0.0, -m)) + 0.5 * lam * w @ w)

    def grad(w):
        m = y * (X @ w)
        s = 0.5 * (1.0 - np.tanh(m / 2.0))  # sigmoid(-m)
        return -(X * (y * s)[:, None]).mean(axis=0) + lam * w

    li, gi = loss(w), grad(w)
    for _ in range(int(cfg["steps"])):
        w = w - cfg["lr"] * grad(w)
    pred = np.where(X @ w >= 0, 1.0, -1.0)
    return {"loss_init": li, "grad_init": gi, "w_final": w,
            "loss_final": loss(w), "train_accuracy": float(np.mean(pred == y))}


def out():
    assert os.path.exists(OUT)
    return json.load(open(OUT))


def test_exists():
    assert os.path.exists(OUT)


def test_schema():
    o = out()
    assert set(o.keys()) == KEYS
    D = np.load(os.path.join(W, "data.npz"))["X"].shape[1]
    assert len(o["grad_init"]) == D and len(o["w_final"]) == D


def test_initial_loss_and_grad():
    o, r = out(), ref()
    assert abs(o["loss_init"] - r["loss_init"]) < 1e-6
    assert np.allclose(np.array(o["grad_init"], float), r["grad_init"], rtol=0, atol=1e-6)


def test_descent_result():
    o, r = out(), ref()
    assert np.allclose(np.array(o["w_final"], float), r["w_final"], rtol=0, atol=1e-6)
    assert abs(o["loss_final"] - r["loss_final"]) < 1e-6


def test_accuracy():
    o, r = out(), ref()
    assert abs(o["train_accuracy"] - r["train_accuracy"]) < 1e-9
