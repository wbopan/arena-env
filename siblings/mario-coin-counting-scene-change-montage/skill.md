## Reference notes

Use **Pillow** (`PIL`), named in the task. Video keyframe extraction and ImageMagick conversions are not needed; Pillow’s `L` conversion defines the required pixel values.

```python
from PIL import Image, ImageChops

with Image.open(path) as im:
    gray = im.convert("L")  # independent 8-bit grayscale image
```

For two same-sized `L` images, `ImageChops.difference(previous, current)` gives each pixel’s absolute difference. Its histogram counts pixels at each difference level:

```python
diff = ImageChops.difference(previous, current)
total = sum(level * count for level, count in enumerate(diff.histogram()))
select = total >= 25 * (32 * 24)  # exact equivalent of mean >= 25.0
```

Keep `previous` as the grayscale **immediately preceding input frame**, updating it even when `current` is not selected. Start the selected list with frame 000.

To assemble selected grayscale images without changing their pixels:

```python
montage = Image.new("L", (32 * len(selected), 24))
for position, gray in enumerate(selected):
    montage.paste(gray, (32 * position, 0))
montage.save(output_path, format="PNG")
```

Read inputs in numeric filename order. Check that each opened image has size `(32, 24)`; after saving, reopen the output to check its mode is `L` and its dimensions match the selected-frame count.
