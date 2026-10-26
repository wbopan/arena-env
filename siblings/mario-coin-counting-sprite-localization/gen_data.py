import random
from pathlib import Path
from PIL import Image

random.seed(4916)
Path('frames').mkdir(exist_ok=True)
names = ('coin', 'enemy', 'turtle')
sprites = {}
for name in names:
    values = random.sample(range(75, 241), 25)
    sprite = Image.new('RGB', (5, 5))
    sprite.putdata([(v, v, v) for v in values])
    sprite.save(name + '.png')
    sprites[name] = sprite

positions = [(4 + col * 12, 4 + row * 15) for row in range(2) for col in range(5)]
for number in (1, 2):
    image = Image.new('RGB', (64, 40), (14 + number, 25 + number, 37 + number))
    for position in random.sample(positions, 7 if number == 1 else 8):
        image.paste(sprites[random.choice(names)], position)
    image.save(f'frames/frame_{number:03d}.png')
