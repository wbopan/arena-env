import numpy as np
from PIL import Image

rng = np.random.default_rng(4242)
W, H = 64, 48
PALETTE = [(92, 148, 252), (0, 0, 0), (220, 220, 220), (252, 188, 60),
           (200, 36, 0), (200, 76, 12), (136, 80, 24), (240, 200, 90)]
SKY, BLACK, LIGHT, COIN, MARIO, BLOCK, GROUND, DECOY = range(8)
flat = [c for col in PALETTE for c in col] + [0] * (768 - 3 * len(PALETTE))

scenes = [SKY, BLACK, LIGHT, BLACK, SKY, LIGHT]
frames, durs = [], []
for bg in scenes:
    length = int(rng.integers(3, 8))
    base = np.full((H, W), bg, dtype=np.uint8)
    base[42:, :] = GROUND
    placed = []

    def place():
        for _ in range(2000):
            y = int(rng.integers(2, 33))
            x = int(rng.integers(1, W - 4))
            if all(max(abs(y - py), abs(x - px)) >= 5 for py, px in placed):
                placed.append((y, x))
                return (y, x)
        return None

    coins = []
    for _ in range(int(rng.integers(1, 9))):
        p = place()
        if p:
            base[p[0]:p[0] + 3, p[1]:p[1] + 3] = COIN
            coins.append(p)
    for color in (BLOCK, DECOY):
        for _ in range(int(rng.integers(1, 4))):
            p = place()
            if p:
                base[p[0]:p[0] + 3, p[1]:p[1] + 3] = color
    grab = int(rng.integers(1, length + 1))
    for t in range(length):
        arr = base.copy()
        if t >= grab and coins:
            y, x = coins[0]
            arr[y:y + 3, x:x + 3] = bg
        mx = 2 + 2 * t
        arr[38:42, mx:mx + 4] = MARIO
        im = Image.frombytes("P", (W, H), np.ascontiguousarray(arr).tobytes())
        im.putpalette(flat)
        frames.append(im)
        durs.append(int(rng.choice([40, 50, 60, 80, 100])))

frames[0].save("level.gif", save_all=True, append_images=frames[1:],
               duration=durs, loop=0, optimize=False, disposal=1)
