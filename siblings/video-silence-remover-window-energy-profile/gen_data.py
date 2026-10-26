import math
import random
import struct
import wave

random.seed(4812)
rate = 800
levels = [random.choice([35, 80, 250, 1100, 2300, 3700]) for _ in range(21)]
samples = []
for level in levels:
    for j in range(rate // 2):
        value = level * math.sin(2 * math.pi * (37 + level % 13) * j / rate)
        value += random.randint(-level // 9, level // 9)
        samples.append(max(-32768, min(32767, round(value))))
with wave.open('lecture_audio.wav', 'wb') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(rate)
    wav.writeframes(struct.pack('<' + 'h' * len(samples), *samples))
