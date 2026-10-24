## Reference notes

Use **NumPy** and `scipy.signal.correlate2d` for the exact sliding-window calculation. The object-counter skill suggests `scripts/count_objects.py --tool count --threshold 0.9 --dedup_min_dist 3`, but use a short local script here so grayscale, zero-variance, and Chebyshev-distance conventions are explicit.

**Reading PNGs:** ImageMagick’s `identify` can report dimensions; `convert` can emit raw, three-channel, 8-bit RGB. Check that both commands are available. Raw `rgb:-` output has no header, so reshape it using the reported height and width.

```python
import subprocess
import numpy as np

def read_rgb(path):
    w, h = map(int, subprocess.check_output(
        ["identify", "-format", "%w %h", str(path)], text=True
    ).split())
    data = subprocess.check_output(
        ["convert", str(path), "-depth", "8", "rgb:-"]
    )
    return np.frombuffer(data, dtype=np.uint8).reshape(h, w, 3)

def luma(rgb):
    return rgb.astype(np.float64) @ np.array([0.299, 0.587, 0.114])
```

Do not round luma. Match each template **as supplied**; flipping it would count mirrored decoys.

For template `t` of shape `(8, 8)`, let `tc = t - t.mean()` and `ones = np.ones(t.shape)`. With `mode="valid"`, each output index is the window’s top-left `(row, column)`:

```python
from scipy.signal import correlate2d

numerator = correlate2d(frame_y, tc, mode="valid")
window_sum = correlate2d(frame_y, ones, mode="valid")
window_sq_sum = correlate2d(frame_y**2, ones, mode="valid")
window_ss = np.maximum(window_sq_sum - window_sum**2 / t.size, 0)
template_ss = np.sum(tc**2)
```

Pearson score is `numerator / sqrt(window_ss * template_ss)`; set it to **0** wherever either sum of squares is zero. `np.divide(..., out=zeros, where=denominator>0)` handles that case. Only scores `>= 0.90` are candidates.

For each frame and sprite type separately, visit candidate `(row, column)` positions in **descending score** order. Keep one only if, for every previously kept position, `max(abs(row−kept_row), abs(column−kept_column)) > 3`. Thus distance **exactly 3** suppresses a candidate. Count kept positions.

Use `sorted(Path("/root/work/frames").glob("frame_*.png"))` for row order. Write CSV with `csv.writer`, header `["frame_id", "coins", "goombas"]`, and `path.name` as `frame_id`; inspect the written file after running the script.
