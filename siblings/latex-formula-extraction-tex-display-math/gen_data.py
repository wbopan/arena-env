import random

random.seed(20240611)

SYM = list("abcdfghkmpqrsuvwxyz")
GREEK = [r"\alpha", r"\beta", r"\gamma", r"\lambda", r"\mu", r"\sigma", r"\omega", r"\theta"]
TEMPLATES = [
    r"@S_{@S} = \frac{@G^{@N}}{@S + @N}",
    r"\sum_{i=1}^{@N} @S_i^{2} = @G @S",
    r"\int_{0}^{@N} @S(t) dt = @G^{@N}",
    r"@G(@S) = \sqrt{@S^{@N} + @G^{2}}",
    r"\mathbf{@S} = \left( @S_1 + @S_2 \right)^{@N}",
    r"P(@S \mid @S) = \frac{P(@S) P(@S)}{@N}",
    r"\lim_{n \to \infty} \left[ 1 + \frac{@G}{n} \right]^{n} = e^{@G}",
    r"\nabla \cdot \mathbf{@S} = \frac{@G}{\epsilon_{@N}}",
    r"@S_{n+1} = @S_n - @G \frac{\partial L}{\partial @S_n}",
]
INLINE = [r"@S_{@N}", r"@G^{@N}", r"@S + @G"]
SENTENCES = [
    "We study the behaviour of ${}$ under small perturbations.",
    "The coefficient ${}$ is estimated from the training data.",
    "Note that ${}$ remains bounded for all admissible inputs.",
    "This motivates the following relation.",
    "Combining the previous results gives the identity below.",
]


def fill(t):
    out = []
    i = 0
    while i < len(t):
        if t.startswith("@S", i):
            out.append(random.choice(SYM))
            i += 2
        elif t.startswith("@G", i):
            out.append(random.choice(GREEK))
            i += 2
        elif t.startswith("@N", i):
            out.append(str(random.randint(2, 9)))
            i += 2
        else:
            out.append(t[i])
            i += 1
    return "".join(out)


def punct():
    return random.choice(["", "", ",", ".", " ,", " ."])


def display(idx):
    f = fill(random.choice(TEMPLATES))
    toks = f.split(" ")
    if len(toks) > 4 and random.random() < 0.5:
        k = random.randint(2, len(toks) - 2)
        body = [" ".join(toks[:k]), " ".join(toks[k:])]
    else:
        body = [f]
    body[-1] = body[-1] + punct()
    ind = ["    " + b for b in body]
    kind = random.choice(["eq", "eqlabel", "eqlabel2", "eqstar", "bracket", "bracket1", "dollar"])
    if kind == "eq":
        out = [r"\begin{equation}"] + ind + [r"\end{equation}"]
    elif kind == "eqlabel":
        out = [r"\begin{equation}\label{eq:%d}" % idx] + ind + [r"\end{equation}"]
    elif kind == "eqlabel2":
        out = [r"\begin{equation}"] + ind + [r"    \label{eq:%d}" % idx, r"\end{equation}"]
    elif kind == "eqstar":
        out = [r"\begin{equation*}"] + ind + [r"\end{equation*}"]
    elif kind == "bracket":
        out = [r"\["] + ind + [r"\]"]
    elif kind == "bracket1":
        out = [r"\[ " + " ".join(body) + r" \]"]
    else:
        out = ["$$"] + ind + ["$$"]
    return out


lines = [r"\documentclass{article}", r"\usepackage{amsmath}", "",
         r"\title{Notes on Iterative Estimators}", r"\begin{document}", r"\maketitle", ""]
idx = 0
for sec in range(1, 5):
    lines.append(r"\section{Part %d}" % sec)
    for j in range(random.randint(2, 4)):
        s1 = random.choice(SENTENCES).format(fill(random.choice(INLINE)))
        s2 = random.choice(SENTENCES).format(fill(random.choice(INLINE)))
        lines.append(s1 + " " + s2)
        idx += 1
        blk = display(idx)
        if idx in (3, 9) or random.random() < 0.1:
            blk = ["% " + b for b in blk]
        if random.random() < 0.2:
            lines.append("% TODO: double-check the constants here")
        lines.extend(blk)
        lines.append("")
lines.append(r"\end{document}")

with open("paper.tex", "w") as fh:
    fh.write("\n".join(lines) + "\n")
