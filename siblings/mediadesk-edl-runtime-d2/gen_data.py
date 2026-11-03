import csv, json, random
random.seed(20261570)
LEVEL = 2


def tc_to_frames(tc, fps, drop):
    sep = ";" if ";" in tc else ":"
    h, m, s, f = [int(x) for x in tc.replace(";", ":").split(":")]
    if not drop:
        return ((h * 60 + m) * 60 + s) * fps + f
    total_min = h * 60 + m
    return ((h * 3600 + m * 60 + s) * 30 + f) - 2 * (total_min - total_min // 10)

def frames_to_tc(n, fps, drop):
    if not drop:
        f = n % fps; s = n // fps
        return "%02d:%02d:%02d:%02d" % (s // 3600, s // 60 % 60, s % 60, f)
    d, m = divmod(n, 17982)
    n += 18 * d + (2 * ((m - 2) // 1798) if m >= 2 else 0)
    f = n % 30; s = n // 30
    return "%02d:%02d:%02d;%02d" % (s // 3600, s // 60 % 60, s % 60, f)


fps = {1: 25, 2: 30, 3: 30}[LEVEL]
drop = LEVEL == 3
rows = []
for i in range(random.randint(8, 14)):
    start = random.randint(0, 3 * 3600 * fps) if not drop else random.randint(0, 107892 * 2)
    if drop and random.random() < 0.5:
        mm = random.randint(1, 59)
        if mm % 10 == 0:
            mm += 1
        start = tc_to_frames("%02d:%02d:59;%02d" % (random.randint(0, 1), mm - 1, random.randint(20, 29)), 30, True)
    length = random.randint(2 * fps, 40 * fps)
    status = "keep"
    if LEVEL >= 2 and random.random() < 0.25:
        status = "skip"
    rows.append({"clip_id": "C%03d" % (i + 1), "reel": "R%d" % random.randint(1, 4),
                 "src_in": frames_to_tc(start, fps, drop), "src_out": frames_to_tc(start + length, fps, drop), "status": status})
fields = ["clip_id", "reel", "src_in", "src_out"] + (["status"] if LEVEL >= 2 else [])
with open("edl.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
json.dump({"fps": fps, "drop_frame": drop}, open("job.json", "w"))
