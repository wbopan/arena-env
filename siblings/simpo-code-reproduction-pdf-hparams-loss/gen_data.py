import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

rng = np.random.default_rng(7)
B = 64
cl = rng.integers(20, 200, B)
rl = rng.integers(20, 200, B)
cavg = rng.normal(-1.1, 0.3, B)
ravg = rng.normal(-1.4, 0.3, B)
np.savez(
    "batch.npz",
    chosen_logps_sum=(cavg * cl).astype(np.float64),
    rejected_logps_sum=(ravg * rl).astype(np.float64),
    chosen_len=cl.astype(np.int64),
    rejected_len=rl.astype(np.int64),
)

lines = [
    "SimPO: Simple Preference Optimization with a Reference-Free Reward",
    "",
    "Section 2.2 Length-normalized reward",
    "For a prompt x and response y with |y| tokens, the implicit reward is",
    "    r(x, y) = (beta / |y|) * log pi(y | x)",
    "where log pi(y | x) is the summed token log-probability of y under the policy.",
    "",
    "Section 2.3 Objective with target reward margin",
    "Let y_w be the winning (chosen) response and y_l the losing (rejected) one.",
    "Define z = r(x, y_w) - r(x, y_l) - gamma.",
    "With label smoothing ls, the per-example loss is",
    "    L = -(1 - ls) * log sigmoid(z) - ls * log sigmoid(-z)",
    "Losses are reported per example, without reduction.",
    "",
    "Table 2: Final hyperparameters",
    "beta = 2.5",
    "gamma = 1.375",
    "label_smoothing = 0.1",
]
c = canvas.Canvas("paper.pdf", pagesize=letter)
w, h = letter
y = h - 72
for ln in lines:
    c.drawString(60, y, ln)
    y -= 18
c.save()
