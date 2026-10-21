import os
import random
import itertools
from fractions import Fraction as F

random.seed(7321)
os.makedirs("cifs", exist_ok=True)
H = F(1, 2)
Z = (F(0), F(0), F(0))


def mk(perm, signs):
    return [(perm[i], signs[i]) for i in range(3)]


def combine(ops, cents):
    out = []
    for c in cents:
        for rows, t in ops:
            out.append((rows, tuple((t[i] + c[i]) % 1 for i in range(3))))
    return out


def op_str(rows, t):
    parts = []
    for i, (ax, sg) in enumerate(rows):
        s = ("-" if sg < 0 else "") + "xyz"[ax]
        if t[i] != 0:
            s += "+" + str(t[i])
        parts.append(s)
    return ", ".join(parts)


p21c = [(mk((0, 1, 2), (1, 1, 1)), Z), (mk((0, 1, 2), (-1, 1, -1)), (F(0), H, H)),
        (mk((0, 1, 2), (-1, -1, -1)), Z), (mk((0, 1, 2), (1, -1, 1)), (F(0), H, H))]
pmmm = [(mk((0, 1, 2), s), Z) for s in itertools.product((1, -1), repeat=3)]
cmmm = combine(pmmm, [Z, (H, H, F(0))])
oh = [(mk(p, s), Z) for p in itertools.permutations(range(3)) for s in itertools.product((1, -1), repeat=3)]
fm3m = combine(oh, [Z, (F(0), H, H), (H, F(0), H), (H, H, F(0))])

Q = F(1, 4)
FILES = [
    ("A_monoclinic.cif", "P 1 21/c 1", p21c, [
        ("Fe1", "Fe", (F(0), F(0), F(0)), 1.0),
        ("Na1", "Na", (H, F(0), H), 1.0),
        ("P1", "P", ("a", "b", "c"), 1.0),
        ("O1", "O", ("a", "b", "c"), 1.0),
        ("O2", "O", ("a", "b", "c"), 0.5),
    ]),
    ("B_orthorhombic.cif", "P m m m", pmmm, [
        ("Ba1", "Ba", (F(0), F(0), F(0)), 1.0),
        ("Cu1", "Cu", (H, H, F(0)), 1.0),
        ("O1", "O", (H, F(0), "c"), 1.0),
        ("O2", "O", ("a", "b", H), 0.5),
        ("Y1", "Y", ("a", "b", "c"), 1.0),
    ]),
    ("C_centered.cif", "C m m m", cmmm, [
        ("Sr1", "Sr", (F(0), F(0), F(0)), 1.0),
        ("Ti1", "Ti", (Q, Q, "c"), 0.75),
        ("O1", "O", ("a", F(0), F(0)), 1.0),
        ("O2", "O", ("a", "b", F(0)), 1.0),
        ("Cl1", "Cl", ("a", "b", "c"), 0.25),
    ]),
    ("D_cubic.cif", "F m -3 m", fm3m, [
        ("Na1", "Na", (F(0), F(0), F(0)), 1.0),
        ("Cl1", "Cl", (H, H, H), 1.0),
        ("F1", "F", (Q, Q, Q), 1.0),
        ("O1", "O", ("a", F(0), F(0)), 1.0),
        ("Li1", "Li", ("a", "a", "a"), 0.5),
        ("K1", "K", ("a", Q, Q), 1.0),
        ("Mg1", "Mg", ("a", "b", "c"), 0.125),
    ]),
]


def rv():
    while True:
        v = random.uniform(0.03, 0.47)
        if abs(v - 0.25) > 0.03:
            return v


def fmt_coord(c, vars_):
    if isinstance(c, F):
        v = float(c)
        if random.random() < 0.2:
            v += random.choice([1.0, -1.0])
        return f"{v:.5f}"
    v = vars_[c]
    r = random.random()
    if r < 0.15:
        v -= 1.0
    elif r < 0.3:
        v += 0.5
    return f"{v:.5f}({random.randint(1, 9)})"


for fname, hm, ops, sites in FILES:
    ops = [ops[0]] + random.sample(ops[1:], len(ops) - 1)
    lines = [f"data_{fname[:-4]}", f"_symmetry_space_group_name_H-M   '{hm}'"]
    a = round(random.uniform(4, 12), 4)
    for ax in "abc":
        lines.append(f"_cell_length_{ax}   {a if hm.startswith('F') else round(random.uniform(4, 12), 4)}")
    beta = round(random.uniform(95, 115), 3) if "21/c" in hm else 90.0
    lines += ["_cell_angle_alpha   90.0", f"_cell_angle_beta   {beta}", "_cell_angle_gamma   90.0", ""]
    lines += ["loop_", "_symmetry_equiv_pos_site_id", "_symmetry_equiv_pos_as_xyz"]
    for i, (rows, t) in enumerate(ops, 1):
        lines.append(f"{i} '{op_str(rows, t)}'")
    lines += ["", "loop_", "_atom_site_label", "_atom_site_type_symbol", "_atom_site_fract_x",
              "_atom_site_fract_y", "_atom_site_fract_z", "_atom_site_occupancy", "_atom_site_U_iso_or_equiv"]
    for label, el, coords, occ in sites:
        vars_ = {"a": rv(), "b": rv(), "c": rv()}
        cs = [fmt_coord(c, vars_) for c in coords]
        lines.append(f"{label} {el} {cs[0]} {cs[1]} {cs[2]} {occ} {random.uniform(0.005, 0.03):.4f}")
    lines.append("")
    with open(os.path.join("cifs", fname), "w") as fh:
        fh.write("\n".join(lines) + "\n")
