import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

random.seed(424242)

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
BODY = [
    "The calibration run used {n} samples from the archive.",
    "Results were checked against the relation in ({r}).",
    "As shown in ({r}), the residual decreases quickly.",
    "Table {n} summarises the measured coefficients.",
    "The model is evaluated on held-out sensor data.",
    "Substituting ({r}) into the update rule yields the next result.",
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


c = canvas.Canvas("tech_note.pdf", pagesize=letter)
eq = 0
for page in range(1, 4):
    c.setFont("Helvetica", 10)
    c.drawString(72, 750, "Technical Note TN-17 - page %d of 3" % page)
    y = 715
    for k in range(random.randint(14, 18)):
        r = random.random()
        if k == 3 or r < 0.25:
            eq += 1
            s = fill(random.choice(TEMPLATES)) + random.choice(["", "", ",", ".", " ,"]) + "          (%d)" % eq
            c.drawString(110, y, s)
        elif r < 0.37:
            s = fill(random.choice(TEMPLATES)) + random.choice(["", ",", "."])
            c.drawString(110, y, s)
        else:
            s = random.choice(BODY).format(n=random.randint(2, 40), r=random.randint(1, max(eq, 1)))
            c.drawString(72, y, s)
        y -= 20
    c.drawString(300, 40, "%d" % page)
    c.showPage()
c.save()
