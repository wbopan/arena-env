1. Print `problem.json` (id, description, input, output), then print only the keys, shapes and dtypes of each input.
2. Write one `solve.py` using plain jax/jnp (don't rely on `jax_skills`) with x64 enabled.
   - Square: vmap. Reduce: `jnp.mean(axis)`.
   - Logistic: `jax.grad` of `mean(logaddexp(0, -y*(x@w)))`.
   - RNN: `lax.scan` with `tanh(x@Wx + h@Wh + b)` and zero h0, returning all states.
3. Save each result via `np.save(np.asarray(res))` to the exact output path, then check shapes and values against a NumPy reference.
