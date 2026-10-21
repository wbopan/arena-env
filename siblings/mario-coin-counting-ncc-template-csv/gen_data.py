import os
import numpy as np
from PIL import Image

rng = np.random.default_rng(20240611)
T = 8
H, W = 60, 80


def luma(a):
    a = a.astype(np.float64)
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def ncc(a, b):
    a = a - a.mean()
    b = b - b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else 0.0


COIN_PAL = np.array([[252, 188, 60], [200, 120, 20], [255, 240, 160], [120, 60, 0]], dtype=np.uint8)
GOOMBA_PAL = np.array([[150, 70, 20], [230, 180, 140], [20, 20, 20], [255, 255, 255]], dtype=np.uint8)

while True:
    coin = COIN_PAL[rng.integers(0, 4, (T, T))]
    goomba = GOOMBA_PAL[rng.integers(0, 4, (T, T))]
    cl, gl = luma(coin), luma(goomba)
    checks = [ncc(cl, gl), ncc(cl, cl[:, ::-1]), ncc(gl, gl[:, ::-1]),
              ncc(cl, cl[::-1, :]), ncc(gl, gl[::-1, :])]
    if max(abs(c) for c in checks) < 0.35:
        break

Image.fromarray(coin, "RGB").save("coin.png")
Image.fromarray(goomba, "RGB").save("goomba.png")


def dim(p):
    return np.clip(p.astype(np.float64) * 0.6 + 30, 0, 255).round().astype(np.uint8)


os.makedirs("frames", exist_ok=True)
for f in range(7):
    img = rng.integers(60, 124, (H, W, 3)).astype(np.uint8)
    items = []
    items += [coin] * int(rng.integers(0, 5))
    items += [dim(coin)] * int(rng.integers(0, 3))
    items += [goomba] * int(rng.integers(0, 4))
    items += [dim(goomba)] * int(rng.integers(0, 2))
    items += [coin[:, ::-1]] * int(rng.integers(0, 3))
    items += [goomba[::-1, :]] * int(rng.integers(0, 2))
    placed = []
    for patch in items:
        for _ in range(2000):
            y = int(rng.integers(0, H - T + 1))
            x = int(rng.integers(0, W - T + 1))
            if all(max(abs(y - py), abs(x - px)) >= T + 2 for py, px in placed):
                placed.append((y, x))
                img[y:y + T, x:x + T] = patch
                break
    Image.fromarray(img, "RGB").save(f"frames/frame_{f + 1:03d}.png")
