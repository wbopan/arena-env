import os
import random

random.seed(20240607)
os.makedirs("project", exist_ok=True)

prefixes = ["geom", "partial", "sum", "pow_half", "tail", "bound", "mono", "succ", "pos", "shift", "scale", "telescope"]
suffixes = ["le", "lt", "eq", "aux", "step", "pos", "nonneg", "mono"]
names = []
seen = set()
while len(names) < 34:
    nm = random.choice(prefixes) + "_" + random.choice(suffixes)
    if nm in seen:
        continue
    seen.add(nm)
    names.append(nm)
for base in random.sample(names, 4):
    names.append(base + "'")
names += ["no_sorry_needed", "sorry_free_bound"]
random.shuffle(names)

kinds = {n: random.choice(["theorem", "theorem", "lemma", "def"]) for n in names}
direct = set(random.sample(names, 6))
tactics = ["  simp", "  linarith", "  norm_num", "  omega", "  positivity", "  ring_nf"]
fnames = ["Basic.lean", "Bounds.lean", "Geom.lean", "Tail.lean"]
files = {fn: [] for fn in fnames}
header = "import Mathlib\n\n-- This project must contain no sorry\nopen Finset\n\n"
files["Basic.lean"].append("def S : \u2115 \u2192 \u211a\n  | 0 => 1\n  | n + 1 => S n + 1 / 2 ^ (n + 1)\n")

for i, n in enumerate(names):
    lines = []
    if random.random() < 0.2:
        lines.append("@[simp]")
    k = kinds[n]
    if k == "def":
        lines.append(f"def {n} (n : \u2115) : \u211a :=")
    else:
        lines.append(f"{k} {n} (n : \u2115) : S n \u2264 2 := by")
    refs = random.sample([m for m in names if m != n], random.choice([0, 1, 1, 2, 2, 3]))
    for j, r in enumerate(refs):
        style = random.random()
        if style < 0.3:
            lines.append(f"  have h{j} := ({r} n).trans le_rfl")
        elif style < 0.6:
            lines.append(f"  have h{j} := {r} (n + 1)")
        else:
            lines.append(f"  rw [{r}]")
    for _ in range(random.randint(1, 3)):
        lines.append(random.choice(tactics))
    if random.random() < 0.35:
        other = random.choice(names)
        lines.append(f"  -- TODO: maybe use {other} instead of sorry")
    if random.random() < 0.15:
        lines.append(f"  -- theorem fake_{i} : True := sorry")
    if n in direct:
        if random.random() < 0.5:
            lines.append("  sorry")
        else:
            lines.append("  exact sorry  -- placeholder")
    lines.append("")
    files[fnames[i % 4]].append("\n".join(lines))

for fn in fnames:
    with open(os.path.join("project", fn), "w", encoding="utf-8") as fh:
        fh.write(header + "\n".join(files[fn]))
