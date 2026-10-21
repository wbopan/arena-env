import json
import numpy as np

rng = np.random.default_rng(31337)
H, W, T, M = 48, 64, 5, 10
canvas = rng.integers(0, 256, size=(H + 2 * M, W + 2 * M))
steps = [(3, 0), (2, -2), (-1, 3), (0, 2)]
cum = [(0, 0)]
for dx, dy in steps:
    cum.append((cum[-1][0] + dx, cum[-1][1] + dy))

frames = np.zeros((T, H, W), dtype=np.uint8)
for t, (cx, cy) in enumerate(cum):
    img = canvas[M - cy:M - cy + H, M - cx:M - cx + W].astype(int)
    img = img + rng.integers(-2, 3, size=(H, W))
    ax, ay = 8 + 5 * t, 10
    img[ay:ay + 7, ax:ax + 7] = 250
    bx, by = 44 - 3 * t, 30 - 2 * t
    img[by:by + 6, bx:bx + 8] = 5
    for _ in range(4):
        py, px = rng.integers(2, H - 2), rng.integers(2, W - 2)
        img[py, px] = 255
    frames[t] = np.clip(img, 0, 255)

np.savez("frames.npz", frames=frames)
with open("shifts.json", "w") as f:
    json.dump([{"frame": t, "dx": dx, "dy": dy} for t, (dx, dy) in enumerate(steps, start=1)], f, indent=1)
