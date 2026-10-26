import random
import wave
import numpy as np

random.seed(4612)
rng = np.random.default_rng(4612)
n = 3600
t = np.arange(n) / 16000
freq = random.choice([179, 211, 257])
voice = 0.105 * np.sin(2 * np.pi * freq * t) + 0.032 * np.sin(2 * np.pi * 2 * freq * t)
left = voice + rng.normal(0, 0.006, n)
right = 0.88 * voice + rng.normal(0, 0.008, n)
stereo = np.column_stack((left, right))
stereo[:100] = 0
stereo[-110:] = 0
pcm = np.rint(np.clip(stereo, -1, 1) * 32768).astype('<i2')
with wave.open('dialogue.wav', 'wb') as out:
    out.setnchannels(2)
    out.setsampwidth(2)
    out.setframerate(16000)
    out.writeframes(pcm.tobytes())
