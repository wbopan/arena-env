**Goal.** Read `problem.json` (usually in the working directory, e.g. /root or /app; find it with `find / -name problem.json 2>/dev/null | head`). It is a list of tasks with the keys `id`, `description`, `input` and `output`. For every task, load the input, compute what the description asks for using JAX, and save the result to the exact `output` path. Resolve that path relative to the directory containing `problem.json`, unless it is absolute. Write `.npy` with `np.save`.

**Inspect cheaply first.**
- `python3 -c "import json;[print(t['id'],'|',t['description'],'|',t['input'],'|',t['output']) for t in json.load(open('problem.json'))]"`
- For each input, print shape and dtype only. Do not print the data.
  - `.npy`: `python3 -c "import numpy as np;a=np.load('data/x.npy');print(a.shape,a.dtype)"`
  - `.npz`: `d=np.load(p); print({k:(d[k].shape,d[k].dtype) for k in d.files})`. The key names (e.g. `x`, `y`, `w`, `seq`, `Wx`, `Wh`, `b`) tell you the arguments.
- Check that JAX imports: `python3 -c "import jax,jax.numpy as jnp;print(jax.__version__)"`.
- The `jax_skills` helper module may not exist. Don't depend on it. Implement everything with plain `jax`/`jnp`.

**Loading and saving.**
- Load with `np.load(path)`. For `.npz`, index by key and convert with `jnp.asarray`.
- Save with `np.save(out, np.asarray(result))`. Use `.npy` unless the output extension says otherwise (`.npz` → `np.savez`, `.json` → `json.dump(result.tolist())`).
- Create the parent directory first with `os.makedirs(os.path.dirname(out) or '.', exist_ok=True)`.

**Precision.** Enable 64-bit before any computation if the inputs are float64: `jax.config.update("jax_enable_x64", True)`. This keeps the input dtype so results match a NumPy reference.

**Canonical implementations from the skill.**
- **Map / square (elementwise via vmap):** `jax.vmap(lambda v: v**2)(x)`, which equals `jnp.square(x)`. Other elementwise ops work the same way (`jnp.exp`, `jnp.sin`, ...).
- **Reduce:** `jnp.mean(x, axis=axis)`. Use the axis the description states. If it says "mean of squares along axis 0", use `jnp.mean(x**2, axis=0)`. Do not keep dims unless asked.
- **Logistic gradient:** the loss is `L(w) = mean(log(1 + exp(-y * (x @ w))))` with labels y ∈ {-1, +1}.
  ```python
  def loss(w, x, y): return jnp.mean(jnp.logaddexp(0., -y*(x@w)))
  g = jax.grad(loss)(w, x, y)   # shape == w.shape
  ```
  - `logaddexp(0, z)` is the numerically stable form of `log(1+exp(z))`.
  - If the description uses labels {0,1} or binary cross-entropy instead, follow the description.
- **RNN scan (tanh, lax.scan, returns all hidden states):**
  ```python
  def rnn(seq, Wx, Wh, b, h0=None):
      h0 = jnp.zeros(Wh.shape[0], seq.dtype) if h0 is None else h0
      def step(h, x_t):
          h = jnp.tanh(x_t @ Wx + h @ Wh + b)
          return h, h
      _, hs = jax.lax.scan(step, h0, seq)
      return hs            # (T, H)
  ```
  - Check the weight orientation from the shapes. If `Wx.shape == (H, D)`, use `Wx @ x_t` instead of `x_t @ Wx`.
  - If `seq` is (T, B, D), make h0 shape (B, H).
  - If `h0` is present in the npz, use it.
  - The description decides whether to return the full sequence or only the final state.
- **JIT:** wrap compute functions with `jax.jit(fn)(*args)`. The results are identical. Avoid Python side effects inside jit/vmap/scan.

**Pitfalls.**
- Read every description literally: axis, keepdims, output shape, mean versus sum, and whether the output is the gradient or the loss.
- The output shape must match what the description implies, and the dtype should usually match the input dtype.
- Convert JAX arrays to NumPy before saving.
- If a task's input is a single `.npy` but the operation needs several arrays, look for extra keys or extra files listed in the description.

**Plan.**
1. Print the task list (1 command).
2. Print the input keys, shapes and dtypes for all inputs in one Python one-liner loop.
3. Write `solve.py`. It holds one function per task id, dispatched on the id or the description keywords, and loops over `problem.json`, computes, and saves.
4. Run it.
5. Verify. For each output, print `np.load(out).shape, dtype` and a few values. Cross-check against a pure NumPy reference, e.g. `np.allclose` with plain numpy mean/square/tanh loop. For the gradient, check against the analytic `-(x.T @ (y*sigmoid(-y*xw)))/n`.
6. Confirm that every listed output file exists at its exact path.
