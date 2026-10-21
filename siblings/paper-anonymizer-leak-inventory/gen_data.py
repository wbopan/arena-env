import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

random.seed(4242)

FIRST = ["Alice", "Bruno", "Chen", "Dana", "Elif", "Farid", "Grace", "Hiro", "Ines", "Jonas",
         "Kavya", "Liam", "Mei", "Nadia", "Omar", "Priya", "Quinn", "Rosa", "Sven", "Tara",
         "Umar", "Vera", "Wei", "Yuki", "Zara"]
LAST = ["Wong", "Okafor", "Lindqvist", "Patel", "Moreau", "Tanaka", "Silva", "Kowalski", "Haddad",
        "Novak", "Brennan", "Iyer", "Fischer", "Castillo", "Nakamura", "Osei", "Ramos", "Duarte",
        "Kim", "Laurent", "Sato", "Weber", "Yilmaz", "Zhou", "Abara", "Petrov", "Mendes", "Holm",
        "Quist", "Varga"]
AFFS = [("Duke University", "duke.edu"), ("Carnegie Mellon University", "cmu.edu"),
        ("Renmin University of China", "ruc.edu.cn"), ("Georgia Institute of Technology", "gatech.edu"),
        ("Adobe Research", "adobe.com"), ("Cornell University", "cornell.edu"),
        ("University of Toronto", "utoronto.ca"), ("Tsinghua University", "tsinghua.edu.cn")]
VENUES = ["ICML 2024", "NeurIPS 2023", "ICLR 2025", "Interspeech 2024", "ACL 2024", "EMNLP 2023"]
TITLES = ["Sparse Token Pruning for Long Context Speech Models",
          "Scaling Laws for Singing Voice Synthesis Data",
          "Evaluating Reasoning in Spoken Dialogue Agents",
          "Adaptive Compression of Audio Language Models"]
WORDS = ["efficient", "robust", "speech", "token", "pruning", "alignment", "evaluation", "scaling",
         "retrieval", "models", "voice", "reasoning", "benchmark", "adaptive", "sparse", "learning",
         "audio", "context", "compression", "agents"]
FILLER = [
    "We study how model capacity interacts with the length of the input context.",
    "Prior work has focused on text, leaving spoken inputs comparatively unexplored.",
    "Our method removes redundant tokens using a lightweight scoring function.",
    "The scoring function is trained jointly with the downstream objective.",
    "We evaluate on four public benchmarks covering diverse acoustic conditions.",
    "Results show consistent gains over strong baselines at equal compute.",
    "Ablations confirm that each component contributes to the final accuracy.",
    "We further analyze failure cases involving overlapping speakers.",
    "Training uses a cosine schedule with linear warmup over the first steps.",
    "All experiments were run three times and we report the mean.",
    "Latency is measured on a single accelerator with batch size one.",
    "The approach requires no changes to the pretrained backbone.",
    "We release configuration files to support reproducibility.",
    "Limitations include reliance on clean transcripts for supervision.",
    "Future work will extend the analysis to multilingual settings.",
    "The pruning ratio is selected on a held out validation split.",
    "We observe diminishing returns beyond a moderate pruning ratio.",
    "Human raters preferred our outputs in a blind listening study.",
    "Memory usage drops substantially for inputs longer than one minute.",
    "The theoretical analysis bounds the error introduced by pruning.",
    "We compare against random and attention based selection rules.",
    "Code and checkpoints will be made available upon publication.",
]
INITIALS = "ABCDEFGHJKLMNPRSTW"


def arx():
    return "%02d%02d.%05d" % (random.randint(19, 25), random.randint(1, 12), random.randint(0, 99999))


def ref_title():
    return " ".join(random.sample(WORDS, random.randint(3, 5))).capitalize()


def render(fn, pages):
    c = canvas.Canvas(fn, pagesize=letter)
    for lines in pages:
        y = 760
        c.setFont("Helvetica", 8)
        for ln in lines:
            c.drawString(40, y, ln)
            y -= 12
        c.showPage()
    c.save()


def make_paper(fn, title):
    n = random.randint(3, 5)
    surnames = random.sample(LAST, len(LAST))
    a_last = surnames[:n]
    others = surnames[n:]
    a_first = random.sample(FIRST, n)
    k = random.randint(2, 3)
    affs = random.sample(AFFS, k)
    markers = []
    for i in range(n):
        ms = {i % k}
        if random.random() < 0.3:
            ms.add(random.randrange(k))
        markers.append(sorted(ms))
    author_line = ", ".join("%s %s [%s]" % (a_first[i], a_last[i], ",".join(str(m + 1) for m in markers[i])) for i in range(n))
    p1 = [title, author_line] + ["[%d] %s" % (j + 1, affs[j][0]) for j in range(k)]
    ce = sorted(random.sample(range(n), random.randint(2, n)))
    emails = ["%s%s@%s" % (a_first[i][0].lower(), a_last[i].lower(), affs[markers[i][0]][1]) for i in ce]
    p1.append("Correspondence: " + ", ".join(emails))
    p1.append("Accepted at " + random.choice(VENUES))
    p1.append("arXiv:%sv%d [cs.LG] preprint version" % (arx(), random.randint(1, 3)))
    p1.append("Abstract")
    body = random.sample(FILLER, 20)
    fi = random.randrange(n)
    body.insert(random.randint(2, 10), "Footnote: implementation questions go to %s.%s@%s or the issue tracker" % (a_first[fi].lower(), a_last[fi].lower(), affs[markers[fi][-1]][1]))
    if random.random() < 0.7:
        body.insert(random.randint(3, 15), "An extended version of this study is available as arXiv:%s." % arx())
    p1 += body[:12]
    p2 = body[12:]
    p2 += ["Acknowledgements", "We thank %s %s and %s %s for helpful discussions." % (random.choice(FIRST), others[0], random.choice(FIRST), others[1])]
    p2.append("References")
    m = random.randint(6, 8)
    s = random.randint(2, 3)
    roles = ["self"] * s + ["dist"] + ["other"] * (m - s - 1)
    random.shuffle(roles)
    pool = others[2:]
    for idx, role in enumerate(roles, 1):
        co = random.sample(pool, random.randint(1, 2))
        auths = ["%s, %s." % (x, random.choice(INITIALS)) for x in co]
        if role == "self":
            i = random.randrange(n)
            auths.insert(random.randint(0, len(auths)), "%s, %s." % (a_last[i], a_first[i][0]))
        elif role == "dist":
            i = random.randrange(n)
            ini = random.choice([c for c in INITIALS if c != a_first[i][0]])
            auths.insert(random.randint(0, len(auths)), "%s, %s." % (a_last[i], ini))
        venue = random.choice(VENUES) if random.random() < 0.5 else "arXiv:%s" % arx()
        p2.append("[%d] %s (%d). %s. %s." % (idx, "; ".join(auths), random.randint(2018, 2025), ref_title(), venue))
    p2 += ["Appendix A: Dataset details",
           "Contact the dataset maintainers at data@%s for access" % affs[0][1],
           "A mirror of the release is listed as arXiv:%s in the archive" % arx()]
    render(fn, [p1, p2])


for num, t in enumerate(random.sample(TITLES, 3), 1):
    make_paper("paper%d.pdf" % num, t)
