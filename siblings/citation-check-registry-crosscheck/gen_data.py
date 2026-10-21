import random
import csv

random.seed(20240611)
A = ["Scalable", "Robust", "Efficient", "Adaptive", "Sparse", "Federated", "Causal", "Probabilistic", "Hierarchical", "Contrastive"]
B = ["Graph", "Transformer", "Kernel", "Bayesian", "Reinforcement", "Diffusion", "Attention", "Tensor", "Spectral", "Variational"]
C = ["Learning", "Inference", "Optimization", "Estimation", "Retrieval", "Segmentation", "Clustering", "Forecasting"]
D = ["for Protein Design", "in Supply Chains", "under Distribution Shift", "for Medical Imaging", "with Noisy Labels", "at Web Scale", "for Planning & Control", "in Search & Ranking"]
SUR = ["Nakamura", "Okafor", "Lindqvist", "Moreau", "Haddad", "Petrov", "Silva", "Chen", "Kowalski", "Brennan", "Ibrahim", "Larsen"]
GIV = ["Aiko", "Chidi", "Elsa", "Luc", "Rana", "Ivan", "Bruna", "Wei", "Marta", "Sean", "Omar", "Freja"]
PFX = ["10.1016/j.patrec", "10.1109/tpami", "10.1145/3580305", "10.1038/s41586", "10.1371/journal.pone"]
VEN = ["Journal of Machine Learning Research", "Pattern Recognition Letters", "Neural Computation", "Data Mining and Knowledge Discovery"]
CONF = ["Proceedings of NeurIPS", "Proceedings of ICML", "Proceedings of KDD", "Proceedings of AAAI"]

seen = set()
recs = []
while len(recs) < 60:
    t = " ".join([random.choice(A), random.choice(B), random.choice(C), random.choice(D)])
    if t in seen:
        continue
    seen.add(t)
    y = random.randint(2012, 2023)
    recs.append({"doi": f"{random.choice(PFX)}.{y}.{len(recs) + 101:04d}", "title": t, "year": y, "first_author": random.choice(SUR)})

with open("registry.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["doi", "title", "year", "first_author"])
    w.writeheader()
    w.writerows(recs)

chosen = random.sample(recs, 28)
cats = ["ok"] * 16 + ["missing_doi"] * 3 + ["unknown_doi"] * 3 + ["title_mismatch"] * 3 + ["year_mismatch"] * 3
random.shuffle(cats)
keys = set()
out = []
for rec, cat in zip(chosen, cats):
    title = rec["title"]
    year = rec["year"]
    doi = rec["doi"]
    if cat == "title_mismatch":
        ws = title.split()
        ws[1] = random.choice([b for b in B if b != ws[1]])
        title = " ".join(ws)
    elif cat == "year_mismatch":
        year += random.choice([-2, -1, 1, 2])
    elif cat == "unknown_doi":
        doi = doi.rsplit(".", 1)[0] + f".{random.randint(9000, 9999)}"
    base = f"{rec['first_author'].lower()}{year}{title.split()[0].lower()}"
    key = base if base not in keys else f"{base}{len(keys)}"
    keys.add(key)
    tex = title.replace("&", "\\&")
    r = random.random()
    if r < 0.3:
        ws = tex.split()
        tex = "{" + ws[0] + "} " + " ".join(x.lower() for x in ws[1:])
    elif r < 0.5:
        tex = "{" + tex + "}"
    elif r < 0.65:
        tex = tex.replace(" ", "  ", 1)
    r = random.random()
    if r < 0.25:
        d = "https://doi.org/" + doi
    elif r < 0.45:
        d = "doi:" + doi
    elif r < 0.6:
        d = doi.upper()
    else:
        d = doi
    etype = random.choice(["article", "inproceedings"])
    lines = [f"@{etype}{{{key},",
             f"  author = {{{rec['first_author']}, {random.choice(GIV)} and {random.choice(SUR)}, {random.choice(GIV)}}},",
             f"  title = {{{tex}}},"]
    if etype == "article":
        lines.append(f"  journal = {{{random.choice(VEN)}}},")
    else:
        lines.append(f"  booktitle = {{{random.choice(CONF)}}},")
    lines.append(f"  year = {year}," if random.random() < 0.5 else f"  year = {{{year}}},")
    if cat != "missing_doi":
        lines.append(f"  doi = {{{d}}},")
    lines.append(f"  pages = {{{random.randint(1, 300)}--{random.randint(301, 600)}}}")
    lines.append("}")
    out.append("\n".join(lines))

with open("refs.bib", "w", encoding="utf-8") as f:
    f.write("\n\n".join(out) + "\n")
