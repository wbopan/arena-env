# Dynamic-object masks after global motion compensation

Inputs:
- `/root/work/frames.npz`: key `"frames"`, a uint8 array of shape (T, H, W) holding grayscale sampled frames from a moving camera.
- `/root/work/shifts.json`: a list of objects `{"frame": t, "dx": int, "dy": int}`, one for each t = 1..T-1. These give the global translation such that static background satisfies `curr[y, x] = prev[y-dy, x-dx]`, where `curr` is frame t and `prev` is frame t-1.

For every frame t >= 1, compute a boolean dynamic-object mask:
1. Motion compensation: set `warped[y, x] = prev[y-dy, x-dx]` wherever that source pixel lies inside the image. Those pixels are *valid*; all other pixels are invalid.
2. Compute `diff = |curr - warped|` using integer arithmetic.
3. Over the valid pixels only, compute `med = median(diff)` and `mad = median(|diff - med|)`. Then `thr = max(20, med + 3*1.4826*mad)`.
4. `raw = valid AND (diff > thr)`.
5. Label the 8-connected components of `raw`. Keep only components with an area of at least 12 pixels; that union is the mask.

Frame 0 has an all-False mask.

Output: write `/root/work/dyn_masks.npz` (numpy `savez`) containing:
- `"shape"`: `[H, W]` as int32.
- For each frame i in 0..T-1, the standard CSR encoding of its mask:
  - `f_{i}_data`: uint8 ones, one per True pixel.
  - `f_{i}_indices`: int32 column indices of the True pixels, in row-major order.
  - `f_{i}_indptr`: row pointers of length H+1, with `indptr[0] = 0` and `indptr[-1]` equal to the number of True pixels.

No other `f_*` keys may be present.
