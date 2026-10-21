import random

random.seed(7)
PLACES = ["gate", "tower", "river", "market", "forest", "inn", "crypt", "hall", "bridge", "camp", "shrine", "dock", "mill", "vault", "garden"]
KINDS = ["Scene", "Talk", "Path", "Choice"]
SPEAKERS = ["Guard", "Mira", "Old Tom", "Captain Vex", "Narrator", "Innkeeper"]
WORDS = "the a we must go now quickly where is your sword gold road night king traveler help never trust me fine stranger".split()
TAGS = ["[Lie] ", "[Attack] ", "[Persuade] ", "[Bribe 50] ", "", "", ""]


def sent():
    s = " ".join(random.choice(WORDS) for _ in range(random.randint(3, 9)))
    s = s[0].upper() + s[1:]
    if random.random() < 0.2:
        s = "Listen: " + s
    return s + random.choice([".", "!", "?", "..."])


n = 45
ids = [PLACES[i % len(PLACES)].capitalize() + random.choice(KINDS) + str(i) for i in range(n)]
out = ["# Dialogue script v2", ""]
for i, sid in enumerate(ids):
    out.append("[" + sid + "]")
    if random.random() < 0.15:
        out.append("# note: revise this section")

    def tgt():
        if random.random() < 0.15:
            return "End"
        return random.choice(ids)

    arrow = lambda: random.choice([" -> ", " -> ", "->", "  ->  "])
    if random.random() < 0.45:
        for k in range(1, random.randint(2, 5) + 1):
            line = str(k) + ". " + random.choice(TAGS) + sent() + arrow() + tgt()
            if random.random() < 0.2:
                line = line + "   "
            out.append(line)
    else:
        out.append(random.choice(SPEAKERS) + ": " + sent() + arrow() + tgt())
    out.append("")
    if random.random() < 0.2:
        out.append("")
with open("script.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
