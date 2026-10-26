from pathlib import Path
from PIL import Image, ImageChops, ImageStat

ROOT = Path('/root/work')
OUT = ROOT / 'scene_montage.png'


def selected_frames():
    frames = [Image.open(ROOT / 'frames' / f'frame_{i:03d}.png').convert('L') for i in range(8)]
    chosen = [frames[0]]
    for previous, current in zip(frames, frames[1:]):
        differences = ImageChops.difference(previous, current)
        mean = ImageStat.Stat(differences).mean[0]
        if mean >= 25.0:
            chosen.append(current)
    return chosen


def test_file_exists():
    assert OUT.is_file()


def test_png_grayscale():
    with Image.open(OUT) as result:
        assert result.format == 'PNG'
        assert result.mode == 'L'


def test_dimensions():
    with Image.open(OUT) as result:
        assert result.size == (32 * len(selected_frames()), 24)


def test_selected_pixels_and_order():
    with Image.open(OUT) as result:
        for index, frame in enumerate(selected_frames()):
            assert result.crop((32 * index, 0, 32 * (index + 1), 24)).tobytes() == frame.tobytes()
