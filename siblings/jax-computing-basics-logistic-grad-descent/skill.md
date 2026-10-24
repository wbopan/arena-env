- Use **NumPy**, not the skill document’s `jax_skills.logistic_grad`: that function covers only the unregularized logistic loss. `np.load` reads the `.npz` arrays; the standard-library `json` module reads the configuration and writes the result.

```python
with np.load("/root/work/data.npz") as data:
    X, y, w0 = data["X"], data["y"], data["w0"]

with open("/root/work/config.json") as f:
    config = json.load(f)
```

- For `m = y * (X @ w)`, compute `log(1 + exp(-m))` as `np.logaddexp(0, -m)` to avoid overflow. The full-batch formulas, including regularization, are:

```python
loss = np.logaddexp(0, -m).mean() + 0.5 * l2 * np.dot(w, w)
p = np.exp(-np.logaddexp(0, m))  # sigmoid(-m), computed stably
grad = -(X.T @ (y * p)) / len(y) + l2 * w
```

- Calculate the initial loss and gradient **before** updating weights. Apply exactly `steps` updates, recomputing the gradient at the current weights each time. Afterward, compute loss at the final weights. For accuracy, predict `+1` when `X @ w_final >= 0`, otherwise `-1`.
- Convert NumPy scalars with `float(...)` and vectors with `.tolist()` before `json.dump`; these produce plain JSON numbers. Do not round the values.
