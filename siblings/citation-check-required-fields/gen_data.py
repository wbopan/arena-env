import random

random.seed(4242)
REQ = {"article": ["author", "title", "journal", "year"],
       "inproceedings": ["author", "title", "booktitle", "year"],
       "book": ["author", "title", "publisher", "year"],
       "misc": ["author", "title", "year"]}
SUR = ["Nakamura", "Okafor", "Lindqvist", "Moreau", "Haddad", "Petrov", "Silva", "Chen", "Kowalski", "Brennan", "Ibrahim", "Larsen"]
GIV = ["A.", "C.", "E.", "L.", "R.", "I.", "B.", "W.", "M.", "S."]
TW = ["Notes", "Theory", "Methods", "Analysis", "Systems", "Design", "Models", "Networks", "Signals", "Markets"]
TA = ["Applied", "Modern", "Statistical", "Computational", "Distributed", "Industrial", "Financial", "Quantum"]
JOUR = ["Journal of Applied Statistics", "Management Science", "Operations Research", "Information Systems"]
CONF = ["Proceedings of the Winter Simulation Conference", "Proceedings of SIGMOD", "Proceedings of HICSS"]
PUB = ["Springer", "Wiley", "Cambridge University Press", "MIT Press"]

keys = set()
out = []
for i in range(36):
    et = random.choice(list(REQ))
    sur = random.choice(SUR)
    y = random.randint(1995, 2023)
    t1 = random.choice(TA)
    t2 = random.choice(TW)
    key = f"{sur.lower()}{y}{t1.lower()}"
    if key in keys:
        key += str(i)
    keys.add(key)
    f = {"author": f"{sur}, {random.choice(GIV)} and {random.choice(SUR)}, {random.choice(GIV)}",
         "title": f"{{{t1}}} {t2} of {random.choice(TA).lower()} {random.choice(TW).lower()}",
         "year": str(y)}
    if et == "article":
        f["journal"] = random.choice(JOUR)
        f["volume"] = str(random.randint(1, 80))
    elif et == "inproceedings":
        f["booktitle"] = random.choice(CONF)
        f["pages"] = f"{random.randint(1, 200)}--{random.randint(201, 400)}"
    elif et == "book":
        f["publisher"] = random.choice(PUB)
        f["address"] = "London"
    else:
        f["note"] = "Technical report"
    raw = {k: "{" + v + "}" for k, v in f.items()}
    if random.random() < 0.55:
        for fld in random.sample(REQ[et], random.choice([1, 1, 2])):
            opts = ["drop", "{}", "{ }", '""']
            if fld == "year":
                opts += ["{n.d.}", "{20l9}", "199", "{19999}"]
            o = random.choice(opts)
            if o == "drop":
                raw.pop(fld)
            else:
                raw[fld] = o
        if et == "article" and "journal" not in raw:
            raw["booktitle"] = "{Workshop on " + t2 + "}"
    if raw.get("year") == "{" + str(y) + "}" and random.random() < 0.5:
        raw["year"] = str(y)
    items = list(raw.items())
    random.shuffle(items)
    tname = random.choice([et, et.capitalize(), et.upper()])
    lines = [f"@{tname}{{{key},"]
    for j, (k, v) in enumerate(items):
        name = k.capitalize() if random.random() < 0.2 else k
        sep = "," if j < len(items) - 1 else ""
        lines.append(f"  {name} = {v}{sep}")
    lines.append("}")
    out.append("\n".join(lines))

with open("library.bib", "w", encoding="utf-8") as fh:
    fh.write("\n\n".join(out) + "\n")
