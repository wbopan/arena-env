import csv
import random

random.seed(20240611)

TEXTS = [
    "Bienvenidos a nuestro canal de cocina.",
    "Hoy vamos a preparar algo muy especial.",
    "Primero, lavamos bien las verduras.",
    "Cortamos la cebolla en trozos pequeños.",
    "Calentamos el aceite en la sartén.",
    "Añadimos el ajo y removemos con cuidado.",
    "Dejamos que todo se dore lentamente.",
    "Ahora incorporamos el arroz y el caldo.",
    "Esperamos unos veinte minutos.",
    "¡Buen provecho a todos!",
]
RANGES = {"pad": (0.55, 0.95), "rate": (1.03, 1.22), "trim": (1.30, 1.70)}


def ts(t):
    ms = int(round(t * 1000))
    return "%02d:%02d:%02d,%03d" % (ms // 3600000, (ms // 60000) % 60, (ms // 1000) % 60, ms % 1000)


kinds = ["pad", "rate", "trim"] * 3 + ["rate"]
random.shuffle(kinds)
seg_blocks, txt_blocks, rows = [], [], []
t = 0.3
for i, kind in enumerate(kinds):
    idx = i + 1
    start = round(t + random.uniform(0.15, 0.9), 3)
    end = round(start + random.uniform(1.2, 3.6), 3)
    t = end
    tts = round((end - start) * random.uniform(*RANGES[kind]), 3)
    rows.append((idx, tts))
    seg_blocks.append("%d\n%s --> %s\n[speech %d]\n" % (idx, ts(start), ts(end), idx))
    js = max(0.0, start + random.uniform(-0.3, 0.3))
    je = end + random.uniform(-0.3, 0.3)
    text = TEXTS[i]
    if len(text) > 30 and random.random() < 0.5:
        words = text.split(" ")
        h = len(words) // 2
        text = " ".join(words[:h]) + "\n" + " ".join(words[h:])
    txt_blocks.append("%d\n%s --> %s\n%s\n" % (idx, ts(js), ts(je), text))

with open("segments.srt", "w", encoding="utf-8") as f:
    f.write("\n".join(seg_blocks))
with open("target_text.srt", "w", encoding="utf-8") as f:
    f.write("\n".join(txt_blocks))
random.shuffle(rows)
with open("tts_durations.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["segment_index", "tts_duration_sec"])
    for idx, d in rows:
        w.writerow([idx, "%.3f" % d])
with open("target_language.txt", "w") as f:
    f.write("es\n")
