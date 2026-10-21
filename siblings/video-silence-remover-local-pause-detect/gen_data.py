import random
import wave

import numpy as np

random.seed(1234)
rng = np.random.default_rng(1234)

SR = 160
N = 60

kinds = []


def speech_block():
    if random.random() < 0.3:
        L = random.randint(6, 9)
        A = random.uniform(3000, 3400)
    else:
        L = random.randint(4, 8)
        A = random.uniform(4200, 5600)
    for _ in range(L):
        kinds.append(("s", A))


while len(kinds) < N:
    speech_block()
    if random.random() < 0.6:
        L = random.randint(2, 5)
    else:
        L = 1
    for _ in range(L):
        kinds.append(("p", 0.0))
kinds = kinds[:N]

t = np.arange(SR) / SR
chunks = []
for k, A in kinds:
    if k == "s":
        f = random.uniform(9, 31)
        ph = random.uniform(0, 6.28)
        x = A * np.sin(2 * np.pi * f * t + ph) + rng.normal(0, 300, SR)
    else:
        x = rng.normal(0, random.uniform(60, 120), SR)
    chunks.append(x)

sig = np.clip(np.round(np.concatenate(chunks)), -32768, 32767).astype("<i2")
with wave.open("lecture_audio.wav", "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(sig.tobytes())
