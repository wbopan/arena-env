import json
import math
import os

import numpy as np

W = "/root/work"
OUT = os.path.join(W, "loss.json")
KEYS = {"seq_logprobs", "policy_loss", "kl", "loss", "clip_fraction"}


def expected():
    lg = np.load(os.path.join(W, "logits.npy"))
    tok = np.load(os.path.join(W, "tokens.npy"))
    mask = np.load(os.path.join(W, "mask.npy")).astype(bool)
    old = np.load(os.path.join(W, "old_logprobs.npy"))
    ref = np.load(os.path.join(W, "ref_logprobs.npy"))
    adv = np.load(os.path.join(W, "advantages.npy"))
    N, T, V = lg.shape
    seq, surrs, kls = [], [], []
    n_tok = 0
    n_clip = 0
    for i in range(N):
        s_lp = 0.0
        s_su = []
        s_kl = []
        for t in range(T):
            if not mask[i, t]:
                continue
            row = lg[i, t]
            lse = math.log(sum(math.exp(x) for x in row))
            lp = row[tok[i, t]] - lse
            s_lp += lp
            r = math.exp(lp - old[i, t])
            rc = min(max(r, 0.8), 1.2)
            s_su.append(min(r * adv[i], rc * adv[i]))
            s_kl.append(lp - ref[i, t])
            n_tok += 1
            if r < 0.8 or r > 1.2:
                n_clip += 1
        seq.append(s_lp)
        surrs.append(sum(s_su) / len(s_su))
        kls.append(sum(s_kl) / len(s_kl))
    pl = -sum(surrs) / N
    kl = sum(kls) / N
    return {
        "seq_logprobs": seq,
        "policy_loss": pl,
        "kl": kl,
        "loss": pl + 0.04 * kl,
        "clip_fraction": n_clip / n_tok,
    }


def load():
    with open(OUT) as f:
        return json.load(f)


def test_exists_and_keys():
    assert os.path.isfile(OUT)
    d = load()
    assert KEYS.issubset(d.keys())


def test_seq_logprobs():
    d = load()
    e = expected()
    got = np.array(d["seq_logprobs"], dtype=float)
    assert got.shape == (len(e["seq_logprobs"]),)
    assert (got <= 0).all()
    assert np.allclose(got, e["seq_logprobs"], atol=1e-6)


def test_policy_loss_and_kl():
    d = load()
    e = expected()
    assert abs(float(d["policy_loss"]) - e["policy_loss"]) < 1e-6
    assert abs(float(d["kl"]) - e["kl"]) < 1e-6


def test_total_loss():
    d = load()
    e = expected()
    assert abs(float(d["loss"]) - e["loss"]) < 1e-6


def test_clip_fraction():
    d = load()
    e = expected()
    assert abs(float(d["clip_fraction"]) - e["clip_fraction"]) < 1e-9
