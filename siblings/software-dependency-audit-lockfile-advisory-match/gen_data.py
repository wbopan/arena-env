import json
import random

random.seed(424242)
NAMES = ["lodash", "minimist", "express", "axios", "semver", "tar", "ip", "qs", "ws",
         "jsonwebtoken", "moment", "debug", "glob", "follow-redirects", "undici", "braces",
         "micromatch", "cookie", "path-to-regexp", "body-parser", "@babel/traverse",
         "@types/node", "nanoid", "ejs", "handlebars"]
CH = "23456789cfghjmpqrvwx"


def rv():
    return (random.randint(0, 3), random.randint(0, 12), random.randint(0, 10))


def s(t):
    return "%d.%d.%d" % t


root = {"name": "webapp", "version": "2.3.0", "dependencies": {}}
packages = {"": root}
installed = {}


def nested(n):
    while True:
        p = random.choice(NAMES)
        if p != n:
            path = "node_modules/%s/node_modules/%s" % (p, n)
            if path not in packages:
                return path


def entry(n, v):
    base = n.split("/")[-1]
    return {"version": s(v),
            "resolved": "https://registry.npmjs.org/%s/-/%s-%s.tgz" % (n, base, s(v)),
            "integrity": "sha512-" + "".join(random.choice("ABCDEFabcdef0123456789") for _ in range(20)),
            "dev": random.random() < 0.3}


for n in NAMES:
    vs = set()
    k = random.choice([1, 1, 2])
    while len(vs) < k:
        vs.add(rv())
    vs = sorted(vs)
    installed[n] = vs
    root["dependencies"][n] = "^" + s(vs[0])
    packages["node_modules/" + n] = entry(n, vs[0])
    for v in vs[1:]:
        packages[nested(n)] = entry(n, v)
for n in random.sample(NAMES, 4):
    packages[nested(n)] = entry(n, installed[n][0])

lock = {"name": "webapp", "version": "2.3.0", "lockfileVersion": 3, "requires": True, "packages": packages}
with open("package-lock.json", "w") as f:
    json.dump(lock, f, indent=1)


def gid():
    return "GHSA-" + "-".join("".join(random.choice(CH) for _ in range(4)) for _ in range(3))


TOPICS = ["prototype pollution", "ReDoS", "path traversal", "command injection", "SSRF", "DoS"]
fixed_scores = [9.0, 7.0, 4.0, 3.9, 6.9, 8.9]
advs = []
for i in range(44):
    if i < 40:
        n = random.choice(NAMES)
    else:
        n = random.choice(["left-pad", "event-stream", "node-serialize", "colors"])
    tgt = random.choice(installed.get(n, [rv()]))
    ranges = []
    for _ in range(random.choice([1, 1, 2])):
        if random.random() < 0.6:
            intro = (0, 0, 0) if random.random() < 0.25 else (tgt[0], max(0, tgt[1] - random.randint(0, 3)), 0)
            fx = (tgt[0], max(0, tgt[1] + random.randint(-1, 2)), random.randint(0, 10))
        else:
            intro = rv()
            fx = rv()
        if fx <= intro:
            fx = (intro[0] + 1, 0, 0)
        ranges.append({"introduced": s(intro), "fixed": None if random.random() < 0.15 else s(fx)})
    if i < len(fixed_scores):
        v3 = fixed_scores[i]
    else:
        v3 = round(random.uniform(1.0, 10.0), 1) if random.random() < 0.8 else None
    v2 = round(random.uniform(1.0, 10.0), 1) if random.random() < 0.5 else None
    advs.append({"id": gid(), "package": n, "summary": "%s in %s" % (random.choice(TOPICS), n),
                 "ranges": ranges, "cvss_v3": v3, "cvss_v2": v2})
with open("advisories.json", "w") as f:
    json.dump({"source": "offline-mirror", "advisories": advs}, f, indent=1)
