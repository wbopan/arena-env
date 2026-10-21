1. Run `pdftotext -layout /root/background.pdf -` to learn the game rules, ranking and tie-breaks, and the encoding of a game.
2. Use a pandas `head`/`shape` on /root/data.xlsx (`header=None`) to see how one game per row is stored.
3. Write a Python `score(game)` that returns a comparable tuple. Pair games (1,2), (3,4)…, count P1 and P2 wins with ties excluded, and hand-check a few pairs.
4. Write only `str(p1-p2)` to /root/answer.txt and `cat` it to confirm.
