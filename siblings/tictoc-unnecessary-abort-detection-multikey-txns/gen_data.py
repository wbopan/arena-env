import random

random.seed(1729)
BASE = 1000000000000
keys = [random.getrandbits(64) for _ in range(20)]
versions = {}
wrows = []
tid = BASE + 1
for k in keys:
    n = random.randint(5, 12)
    w = random.randint(1, 50)
    a = random.randint(1, 10)
    vs = []
    for _ in range(n):
        w += random.randint(2, 25)
        a += random.randint(3, 9)
        vs.append((w, a))
        wrows.append((tid, k, w, a))
        tid += 1
    versions[k] = vs
random.shuffle(wrows)

arows = []
atid = BASE + 500001
for t in range(60):
    nrows = random.choice([1, 1, 2, 2, 3])
    ks = random.sample(keys, nrows)
    bias = 0.5 if nrows == 1 else 0.85
    for k in ks:
        vs = versions[k]
        i = random.randint(0, len(vs) - 2)
        j = random.randint(i + 1, len(vs) - 1)
        lw = vs[i][0]
        succ = vs[i + 1][0]
        cw = vs[j][0]
        ats = vs[j][1] + random.randint(1, 2)
        r = random.random()
        if r < 0.08:
            c = succ
        elif r < bias:
            c = random.randint(lw + 1, succ - 1)
        else:
            c = succ + random.randint(1, 40)
        arows.append((atid, k, lw, cw, c, ats))
    atid += random.randint(1, 7)
random.shuffle(arows)

with open("writes.tsv", "w") as f:
    for r in wrows:
        f.write("\t".join(map(str, r)) + "\n")
with open("aborts.tsv", "w") as f:
    for r in arows:
        f.write("\t".join(map(str, r)) + "\n")
