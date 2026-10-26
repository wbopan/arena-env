import random
from pathlib import Path
from PIL import Image

random.seed(8127)
Path('frames').mkdir(exist_ok=True)
levels = [24, 25, 24, 118, 119, 207, 206, 208]
for index, level in enumerate(levels):
    image = Image.new('RGB', (32, 24), (level, level + 2, level + 4))
    # The small moving marker does not itself constitute a scene change.
    x = 2 + index * 3
    y = 4 + (index % 3) * 5
    for dy in range(4):
        for dx in range(4):
            image.putpixel((x + dx, y + dy), (244, 190, 35))
    image.save(f'frames/frame_{index:03d}.png')
