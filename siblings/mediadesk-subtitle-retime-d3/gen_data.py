import json, random
random.seed(20261719)
LEVEL = 3
LINES = ["Welcome back to the workshop.", "Today we restore an old radio.", "First, unplug everything.",
         "Check the capacitors for bulges.", "This one has clearly failed.", "We desolder it carefully.",
         "Mind the polarity on the new part.", "Now the dial cord is next.", "It slips on the pulley.",
         "A drop of glue fixes that.", "Let us power it up slowly.", "Hear that? It hums again.",
         "The tuning is a little off.", "Adjust the trimmer by a hair.", "Much better now.",
         "Thanks for watching, see you soon.", "Subscribe for the next build.", "Bring your own radios!"]
def fmt(ms):
    return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)
n = random.randint(12, 18)
t = random.randint(300, 2500)
cues = []
for i in range(n):
    if LEVEL >= 3 and random.random() < 0.35:
        t += random.randint(10, 70)
    else:
        t += random.randint(150, 900)
    d = random.randint(900, 3400)
    txt = [LINES[i % len(LINES)]]
    if random.random() < 0.3:
        txt.append("(" + random.choice(["music", "laughs", "static", "door closes"]) + ")")
    cues.append((i + 1, t, t + d, txt))
    t += d
order = list(range(n))
if LEVEL >= 2:
    k = random.randint(2, n - 3)
    order[k], order[k + 1] = order[k + 1], order[k]
with open("input.srt", "w", encoding="utf-8") as f:
    f.write("\n".join("%d\n%s --> %s\n%s\n" % (cues[j][0], fmt(cues[j][1]), fmt(cues[j][2]), "\n".join(cues[j][3])) for j in order))
job = {"offset_ms": random.choice([-1, 1]) * random.randint(400, 2600)}
if job["offset_ms"] < 0 and random.random() < 0.6:
    job["offset_ms"] = -(cues[0][2] + random.randint(50, 400))
if LEVEL >= 2:
    job["source_fps"], job["target_fps"] = "23.976", "25"
    job["scale_num"], job["scale_den"] = 24000, 25025
if LEVEL >= 3:
    job["min_gap_ms"] = 80
json.dump(job, open("job.json", "w"), indent=1)
