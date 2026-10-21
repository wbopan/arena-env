**Tools.** Use Python with `cv2`, `numpy` and `json`. Read the video with `cv2.VideoCapture('/root/input.mp4')` and get `n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))`, `fps = cap.get(cv2.CAP_PROP_FPS)`, H and W. Prefer reading the actual frames over trusting `n`. Never print whole frames or arrays; print only shapes, counts and a few statistics.

**Sampling (fps = 5).**
- Compute `step = max(1, round(fps/5))` and keep original frames `0, step, 2*step, …` (all less than the true frame count).
- Sample index `i` is the position in this sampled list (0..N-1). It is not the original frame number.
- Both outputs use sample indices.
- Read sequentially with `cap.read()` and keep a frame when `frame_idx % step == 0`. This is more reliable than seeking.
- Convert each kept frame to gray with `cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)`.

**Egomotion between consecutive samples (i → i+1).**
- Track points:
  ```python
  p0 = cv2.goodFeaturesToTrack(g0, maxCorners=1000, qualityLevel=0.01, minDistance=7)
  p1, st, _ = cv2.calcOpticalFlowPyrLK(g0, g1, p0, None, winSize=(21,21), maxLevel=3)
  ```
  Keep only points where `st == 1`.
- Fit a robust transform: `M, inl = cv2.estimateAffinePartial2D(p0g, p1g, method=cv2.RANSAC, ransacReprojThreshold=3)`.
  - If there are fewer than about 10 points or `M is None`, fall back to the identity `np.float32([[1,0,0],[0,1,0]])`.
- Decompose M:
  - `scale = hypot(M[0,0], M[1,0])`
  - `rot = atan2(M[1,0], M[0,0])` (radians)
  - `dx = M[0,2]`, `dy = M[1,2]`
  - For less sensitivity to zoom-induced translation, you can instead use the median flow of inlier points for dx and dy.
- Direction conventions (image content motion maps to camera motion):
  - Content shifts right (dx > 0) → **Pan Left**; dx < 0 → **Pan Right**.
  - Content shifts down (dy > 0) → **Tilt Up**; dy < 0 → **Tilt Down**.
  - scale > 1 (content expands) → **Dolly In**; scale < 1 → **Dolly Out**.
  - rot > 0 → **Roll Right**; rot < 0 → **Roll Left**.
- Multi-label rule, per the skill:
  ```python
  lbl = []
  if abs(scale-1) > th_scale: lbl.append("Dolly In" if scale > 1 else "Dolly Out")
  if abs(rot) > th_rot: lbl.append("Roll Right" if rot > 0 else "Roll Left")
  if abs(dx) > th_t and abs(dx) >= abs(dy): lbl.append("Pan Left" if dx > 0 else "Pan Right")
  if abs(dy) > th_t and abs(dy) > abs(dx): lbl.append("Tilt Up" if dy > 0 else "Tilt Down")
  if not lbl: lbl = ["Stay"]
  ```
- Thresholds must be scaled to resolution and the 5 fps step. These are starting points only; inspect the printed distributions of dx, dy, rot and scale and adjust:
  - `th_t ≈ 0.005–0.01*W` px per sample
  - `th_rot ≈ 0.3–0.5°` (≈0.005–0.009 rad)
  - `th_scale ≈ 0.005–0.01`
- Labels for frames:
  - Motion i→i+1 labels sample i.
  - The last sample N-1 copies the label of sample N-2.
  - If N == 1, label it `["Stay"]`.
- Smoothing: apply a windowed mode (window 3–5) over the per-frame label tuples to reduce flicker. Never emit an empty list.

**Interval compression (half-open).**
- Merge runs of identical label sets. A run covering samples s..e-1 becomes key `f"{s}->{e}"`, for example `"0->1"` covers only sample 0.
- Intervals must be contiguous and start at 0. The last key ends at N.
- Values are lists of strings from the allowed set only: Stay, Dolly In, Dolly Out, Pan Left, Pan Right, Tilt Up, Tilt Down, Roll Left, Roll Right.
- Write with `json.dump(d, open('/root/pred_instructions.json','w'), indent=2)`.

**Dynamic masks (one per sample, i = 0..N-1).**
- For sample i, align the previous sample (i-1) to i using the same LK + `estimateAffinePartial2D` estimate.
  - For i = 0, use sample 1 as the reference with transform 1→0.
  - If N == 1, store an empty mask.
- Warp and difference:
  ```python
  wp = cv2.warpAffine(prev, M, (W,H), flags=cv2.INTER_LINEAR, borderValue=0)
  valid = cv2.warpAffine(np.ones((H,W),np.uint8), M, (W,H), flags=cv2.INTER_NEAREST) > 0
  valid = cv2.erode(valid.astype(np.uint8), np.ones((5,5),np.uint8)) > 0   # avoid border artifacts
  diff = cv2.absdiff(curr, wp)
  v = diff[valid]; med = np.median(v); mad = np.median(np.abs(v - med))
  thr = max(20, med + 3*1.4826*mad)
  raw = (diff > thr) & valid
  ```
  Compute threshold statistics only on the valid region.
- Clean up: `MORPH_OPEN` with a 3×3 kernel, then `MORPH_CLOSE` with a 7×7 kernel. Then run `connectedComponentsWithStats(..., connectivity=8)` and keep components with area ≥ `min_area` (about 0.001–0.002 of H*W).
- Optionally blur gray frames (GaussianBlur 5×5) before differencing to cut noise.
- CSR encoding of the bool mask `m` (H×W, at full video resolution):
  ```python
  rows, cols = np.nonzero(m)
  out[f"f_{i}_data"] = np.ones(rows.size, np.uint8)
  out[f"f_{i}_indices"] = cols.astype(np.int32)
  out[f"f_{i}_indptr"] = np.concatenate([[0], np.cumsum(np.bincount(rows, minlength=H))]).astype(np.int32)
  ```
  `np.nonzero` returns row-major order, so the indices are already sorted per row.
- Save with `out["shape"] = np.array([H, W], np.int32)` and `np.savez_compressed('/root/pred_dyn_masks.npz', **out)`.
- Use exactly N frames with consecutive keys and no extras.

**Plan (few commands).**
1. Check metadata cheaply:
   `python -c "import cv2;c=cv2.VideoCapture('/root/input.mp4');print(c.get(7),c.get(5),c.get(3),c.get(4))"`
   This prints frame count, fps, width and height. Also confirm `cv2` imports.
2. Write `/root/solve.py` in one heredoc. It should:
   - sample frames;
   - compute the per-pair transform once and reuse it for both labels and masks;
   - print summary statistics (percentiles of dx, dy, rot, scale), the label counts and the mean mask fraction;
   - write both files.
3. Run it and inspect the statistics. If nearly everything is Stay or nearly everything is moving, re-tune thresholds and rerun. If mask fraction is above ~30% or zero everywhere, adjust the mask threshold or `min_area`.
4. Validate with a short script:
   - Keys match `^\d+->\d+$`, intervals are contiguous from 0 to N, and labels are in the allowed set and non-empty.
   - The NPZ has `shape` equal to [H, W] and frames `f_0..f_{N-1}` with all three keys.
   - `len(indptr) == H+1`, `indptr[-1] == indices.size`, and `0 <= indices < W`.

**Output requirements.**
- `/root/pred_instructions.json`: a dict mapping `"start->end"` (half-open, sample indices) to a list of label strings.
- `/root/pred_dyn_masks.npz`: `shape` = [H, W], plus `f_{i}_data`, `f_{i}_indices`, `f_{i}_indptr` for every sampled frame i.
