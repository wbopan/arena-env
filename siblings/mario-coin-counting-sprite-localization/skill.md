## Reference notes

Use Pillow (`PIL.Image`) for exact pixel matching. The object-counting CLI’s threshold and deduplication options are inappropriate here: every exact matching 5×5 region counts, including overlapping regions.

```python
from PIL import Image

with Image.open(path) as im:
    gray = im.convert("L")  # convert screenshots and references the same way
    pixels = gray.load()    # pixels[x, y]
```

For each frame of width `W`, height `H`, and each 5×5 reference, check every upper-left coordinate with `x in range(W - 5 + 1)` and `y in range(H - 5 + 1)`. Compare all 25 grayscale pixel values exactly; do not resize, rotate, reflect, apply a threshold, or suppress nearby matches. A match’s location is `(x, y)`, not its center.

Write with the standard-library `csv` module, opening the output as `open(path, "w", encoding="utf-8", newline="")`. Use `csv.writer`, write `["frame", "x", "y", "kind"]`, and sort detection tuples by `(frame_filename, numeric_y, numeric_x)` before writing. Use input basenames rather than full paths.
