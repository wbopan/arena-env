from pathlib import Path
import wave
import numpy as np

ROOT = Path('/root/work')
OUT = ROOT / 'mastered.wav'


def expected():
    with wave.open(str(ROOT / 'dialogue.wav'), 'rb') as f:
        frames = np.frombuffer(f.readframes(f.getnframes()), dtype='<i2').reshape(-1, 2).astype(np.float64)
    mono = (frames[:, 0] + frames[:, 1]) / 65536.0
    active = mono[np.abs(mono) >= 0.015]
    rms = np.sqrt(np.mean(active * active))
    gain = min(10 ** (-20 / 20) / rms, 10 ** (-3 / 20) / np.max(np.abs(mono)))
    result = mono * gain
    for j in range(80):
        result[j] *= j / 80
        result[-1-j] *= j / 80
    return np.clip(np.rint(result * 32768), -32768, 32767).astype('<i2')


def output():
    with wave.open(str(OUT), 'rb') as f:
        return (f.getnchannels(), f.getsampwidth(), f.getframerate(), f.getnframes(),
                np.frombuffer(f.readframes(f.getnframes()), dtype='<i2'))


def test_exists():
    assert OUT.is_file()


def test_format():
    assert output()[:3] == (1, 2, 16000)


def test_frame_count():
    assert output()[3] == len(expected())


def test_normalized_samples():
    assert np.array_equal(output()[4], expected())


def test_peak_limit():
    assert np.max(np.abs(output()[4].astype(np.int32))) / 32768 <= 10 ** (-3 / 20) + 1 / 32768
