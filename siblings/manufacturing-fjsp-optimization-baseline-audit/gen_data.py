import random, json, csv

random.seed(4242)
J, M = 7, 4
jobs = []
for j in range(J):
    ops = []
    for o in range(random.randint(3, 4)):
        ms = sorted(random.sample(range(1, M + 1), random.randint(1, 3)))
        ops.append([(m, random.randint(2, 9)) for m in ms])
    jobs.append(ops)

with open("instance.txt", "w") as f:
    print(J, M, file=f)
    for ops in jobs:
        parts = [len(ops)]
        for opts in ops:
            parts.append(len(opts))
            for m, d in opts:
                parts += [m, d]
        print(" ".join(map(str, parts)), file=f)

with open("downtime.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["machine", "start", "end"])
    for m in range(1, M + 1):
        for _ in range(random.randint(1, 2)):
            s = random.randint(3, 40)
            w.writerow([m, s, s + random.randint(2, 6)])

mfree = {m: 0 for m in range(1, M + 1)}
jr = [0] * J
rows = []
for o in range(4):
    for j in range(J):
        if o >= len(jobs[j]):
            continue
        m, d = random.choice(jobs[j][o])
        s = max(jr[j], mfree[m])
        rows.append({"job": j, "op": o, "machine": m, "start": s, "end": s + d, "dur": d})
        jr[j] = s + d
        mfree[m] = s + d

idx = list(range(len(rows)))
random.shuffle(idx)
ill = [i for i in idx if len(jobs[rows[i]["job"]][rows[i]["op"]]) < M][:2]
for i in ill:
    r = rows[i]
    allowed = {m for m, _ in jobs[r["job"]][r["op"]]}
    r["machine"] = random.choice([m for m in range(1, M + 1) if m not in allowed])
rest = [i for i in idx if i not in ill]
for i in rest[:2]:
    r = rows[i]
    r["dur"] += random.randint(1, 2)
    r["end"] = r["start"] + r["dur"]
for i in rest[2:6]:
    r = rows[i]
    r["start"] = max(0, r["start"] - random.randint(1, 4))
    r["end"] = r["start"] + r["dur"]
r0 = next(r for r in rows if r["job"] == 0 and r["op"] == 0)
r1 = next(r for r in rows if r["job"] == 0 and r["op"] == 1)
r1["start"] = r0["end"] - 2
r1["end"] = r1["start"] + r1["dur"]
random.shuffle(rows)
with open("baseline_solution.json", "w") as f:
    json.dump({"schedule": rows}, f, indent=1)
