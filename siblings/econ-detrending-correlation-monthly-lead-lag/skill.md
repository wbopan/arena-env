### Reference notes

Use `pandas` for CSV I/O and sorting, `numpy` for logs and correlations, and `scipy.sparse` for the HP-filter linear system. Sort by `month` **before** transforming or filtering; zero-padded `YYYY-MM` strings sort chronologically.

```python
df = pd.read_csv("/root/work/indicators.csv").sort_values("month").reset_index(drop=True)
ip = np.log(df["ip_index"].to_numpy(dtype=float))
payroll = np.log(df["payroll_thousands"].to_numpy(dtype=float))
unrate = df["unemployment_rate"].to_numpy(dtype=float)  # rate: do not log
```

The HP trend solves `(I + λ DᵀD) τ = y`, where each row of `D` takes a second difference: `τ[t] - 2τ[t+1] + τ[t+2]`. The cycle is `y - τ`. For monthly data here, use `λ = 14400`.

```python
from scipy.sparse import diags, eye
from scipy.sparse.linalg import spsolve

def hp_cycle(y, lam=14400):
    n = len(y)
    D = diags(
        [np.ones(n-2), -2*np.ones(n-2), np.ones(n-2)],
        [0, 1, 2], shape=(n-2, n), format="csc"
    )
    trend = spsolve(eye(n, format="csc") + lam * (D.T @ D), y)
    return y - trend
```

For lag `k`, correlate IP at `t` with the other cycle at `t+k`. Use positional NumPy slices to avoid pandas index alignment:

```python
# x = IP cycle; z = other cycle; T = len(x)
if k >= 0:
    a, b = x[:T-k], z[k:]
else:
    a, b = x[-k:], z[:T+k]
corr = np.corrcoef(a, b)[0, 1]
```

This uses exactly `T - abs(k)` pairs. Write lags in ascending order with columns exactly `lag,corr_payroll,corr_unrate`; `DataFrame.to_csv(path, index=False, float_format="%.4f")` writes correlations to four decimal places.
