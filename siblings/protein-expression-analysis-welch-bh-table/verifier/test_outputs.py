import os
import math
import numpy as np
import pandas as pd
from scipy.stats import t as tdist

IN = "/root/work/protein_expression.xlsx"
OUT = "/root/work/results.csv"
COLS = ["protein_id", "mean_control", "mean_treated", "log2fc", "p_value", "q_value", "significant"]


def expected():
    d = pd.read_excel(IN, sheet_name="Data")
    g = pd.read_excel(IN, sheet_name="Design")
    ctrl = [s for s, k in zip(g["Sample"], g["Group"]) if k == "Control"]
    trt = [s for s, k in zip(g["Sample"], g["Group"]) if k == "Treated"]
    rows = []
    for _, r in d.iterrows():
        x = np.array([float(r[s]) for s in trt])
        y = np.array([float(r[s]) for s in ctrl])
        mx, my = x.mean(), y.mean()
        vx, vy = x.var(ddof=1) / len(x), y.var(ddof=1) / len(y)
        tt = (mx - my) / math.sqrt(vx + vy)
        df = (vx + vy) ** 2 / (vx ** 2 / (len(x) - 1) + vy ** 2 / (len(y) - 1))
        p = 2 * tdist.sf(abs(tt), df)
        rows.append([str(r["Protein_ID"]), my, mx, mx - my, p])
    m = len(rows)
    order = sorted(range(m), key=lambda i: rows[i][4])
    q = [0.0] * m
    prev = 1.0
    for rank in range(m, 0, -1):
        i = order[rank - 1]
        val = min(prev, rows[i][4] * m / rank, 1.0)
        q[i] = val
        prev = val
    for i in range(m):
        rows[i].append(q[i])
        rows[i].append("yes" if q[i] < 0.05 and abs(rows[i][3]) >= 1 else "no")
    return rows


def load():
    return pd.read_csv(OUT, dtype={"protein_id": str})


def test_file_exists():
    assert os.path.exists(OUT)


def test_columns_and_order():
    df = load()
    assert list(df.columns) == COLS
    exp = expected()
    assert df["protein_id"].astype(str).str.strip().tolist() == [r[0] for r in exp]


def test_means_and_fold_change():
    df = load()
    exp = expected()
    for k, col in [(1, "mean_control"), (2, "mean_treated"), (3, "log2fc")]:
        assert np.allclose(df[col].astype(float).values, [r[k] for r in exp], atol=1e-5), col


def test_p_values():
    df = load()
    exp = expected()
    assert np.allclose(df["p_value"].astype(float).values, [r[4] for r in exp], rtol=1e-4, atol=1e-10)


def test_q_values():
    df = load()
    exp = expected()
    assert np.allclose(df["q_value"].astype(float).values, [r[5] for r in exp], rtol=1e-4, atol=1e-10)


def test_significance_flags():
    df = load()
    exp = expected()
    assert df["significant"].astype(str).str.strip().str.lower().tolist() == [r[6] for r in exp]
