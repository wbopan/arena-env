import random
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

random.seed(20240611)
N = 200
rows = [(g, random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)) for g in range(1, N + 1)]
random.shuffle(rows)

wb = Workbook()
ws = wb.active
ws.title = "Games"
ws.append(["Game", "Die1", "Die2", "Die3"])
for r in rows:
    ws.append(list(r))
wb.save("data.xlsx")

lines = [
    "Triad Dice Tournament - Scoring Rules",
    "",
    "Each game consists of a single throw of three six-sided dice (Die1, Die2, Die3).",
    "The game score is determined by the highest-ranking category the throw satisfies:",
    "1. Triple (all three dice show the same face): score = 300 + face value.",
    "2. Straight (three consecutive faces in any order, e.g. 3-4-5): score = 200 + highest face.",
    "3. Pair (exactly two dice match): score = 100 + 10 x pair face + remaining (kicker) face.",
    "4. Otherwise (high card): score = sum of the three faces.",
    "",
    "In a match, the game with the higher score wins.",
    "Equal scores are a tie (no winner).",
]
c = canvas.Canvas("background.pdf", pagesize=letter)
y = 740
for line in lines:
    c.drawString(50, y, line)
    y -= 18
c.save()
