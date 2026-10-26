## Reference notes

Use **NumPy** for these local `.npz` arrays; ObsPy and seismic picking models are unnecessary because the task specifies the matching rule.

- Inspect cheaply: `with np.load(path) as z: print(z.files, [(k, z[k].shape) for k in z.files])`. Access arrays by key, e.g. `z["data"]`, `z["p_template"]`.
- A NumPy scalar string can be extracted with `.item()`. For `channels`, decode if the result is `bytes`, then split on commas. Reorder record columns using indices looked up in the template channel list; do this **before** forming windows.
- If a template has `L` rows and a reordered record has `N` rows, complete windows start at `0, …, N-L` (`range(N-L+1)`). Each window is `data[i:i+L, :]`; its pick index is `i`.
- Flatten both arrays in row-major order with `.ravel(order="C")`. For flattened window `w` and template `t`, compute
  `np.dot(w, t) / (np.linalg.norm(w) * np.linalg.norm(t))`.
  Do **not** demean or take the absolute value. `np.argmax(scores)` returns the first maximum, giving the smaller index on an exact tie.
- `dt` is in seconds but is not needed for a sample-index pick. Write CSV with `csv.writer`, header `file_name,phase,pick_idx,score`, basename via `Path(path).name`, and score formatting `f"{score:.4f}"`. Iterate over `sorted(Path("/root/work").glob("record_*.npz"))` and emit P before S for each file.
