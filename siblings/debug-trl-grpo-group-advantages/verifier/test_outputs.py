import os

import numpy as np
import pandas as pd

WORK = "/root/work"
OUT = os.path.join(WORK, "advantages.csv")


def expected():
    df = pd.read_csv(os.path.join(WORK, "rewards.csv"))
    df["reward"] = df["correctness"] * 1.0 + df["format"] * 0.2
    g = df.groupby("prompt_id")["reward"]
    mu = g.transform("mean")
    sd = g.transform(lambda s: s.std(ddof=1))
    df["advantage"] = (df["reward"] - mu) / (sd + 1e-4)
    df["prompt_id"] = df["prompt_id"].astype(str)
    return df.sort_values(["prompt_id", "completion_id"]).reset_index(drop=True)


def load():
    return pd.read_csv(OUT, dtype={"prompt_id": str})


def test_file_exists():
    assert os.path.isfile(OUT)


def test_header():
    with open(OUT) as f:
        header = f.readline().strip()
    assert header == "prompt_id,completion_id,reward,advantage"


def test_rows_and_order():
    out = load()
    exp = expected()
    assert len(out) == len(exp)
    assert list(out["prompt_id"]) == list(exp["prompt_id"])
    assert list(out["completion_id"].astype(int)) == list(exp["completion_id"])


def test_rewards():
    out = load()
    exp = expected()
    assert np.allclose(out["reward"].values, exp["reward"].values, atol=1e-5)


def test_advantages():
    out = load()
    exp = expected()
    diff = np.abs(out["advantage"].values - exp["advantage"].values)
    assert diff.max() < 1e-4, f"max diff {diff.max()}"


def test_constant_groups_zero():
    out = load()
    for pid in ["p003", "p011", "p022"]:
        vals = out.loc[out["prompt_id"] == pid, "advantage"].values
        assert len(vals) == 8 and np.allclose(vals, 0.0, atol=1e-6)
