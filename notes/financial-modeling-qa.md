**Goal.** Read the game or scoring rules from /root/background.pdf. Score every game (row) in /root/data.xlsx using those rules. Pair game 1 with game 2, game 3 with game 4, and so on: odd-numbered games are Player 1, even-numbered games are Player 2. Count the matches each player wins, then write `P1_wins - P2_wins` as a bare number to /root/answer.txt.

**1. Read the background PDF first.** It defines what a "game" is and how one game beats another (hand ranking, score, tie-breaks). Extract all of its text. It is usually short, but check the length before printing:
```bash
pdftotext -layout /root/background.pdf /tmp/bg.txt; wc -l /tmp/bg.txt; head -150 /tmp/bg.txt
```
Fallback:
```python
import pdfplumber
t = "\n".join(p.extract_text() or "" for p in pdfplumber.open("/root/background.pdf").pages)
```
If it contains tables (ranking or payout tables), use `page.extract_tables()`.

Note these points exactly, since they decide the answer:
- the ranking order of outcomes;
- how ties within the same category are broken (kickers, highest card or value, sums);
- what happens on a full tie (counts for neither player);
- any special cases, such as ace high/low, wild values, or bonuses.

**2. Inspect the Excel file cheaply.** Never print the whole sheet.
```python
import pandas as pd
x = pd.read_excel('/root/data.xlsx', sheet_name=None, header=None)
for k, d in x.items(): print(k, d.shape); print(d.head(8).to_string())
```
Determine the following:
- which sheet holds the data;
- whether there is a header row;
- whether there is a game-number column;
- how one game is encoded (one row per game? several columns of cards or dice? one string cell?).

Also check:
- the tail with `d.tail(5)`, to spot totals or blank rows;
- the distinct values in the value columns (`pd.unique(d.iloc[:,c].dropna())`), to learn the encoding, e.g. "10" vs "T", suits, or numbers stored as floats.

If there is a game-number column, use it to determine odd/even, not the row position. Sort by it if needed. Drop fully empty rows. If the count of games is odd, the last game is unpaired, so ignore it.

**3. Write one script, /root/solve.py.** It should:
- load the rows into a list of games in game-number order;
- define `score(game)`, which returns a comparable tuple: `(category_rank, tiebreak1, tiebreak2, ...)`, following the PDF exactly;
- loop `for i in range(0, n-1, 2)`, with `a = score(g[i])` for game 1, 3, 5… and `b = score(g[i+1])`;
  - if `a > b`, increment p1;
  - if `b > a`, increment p2;
  - otherwise it is a tie and counts for neither;
- print n, p1, p2, the tie count, and a few sample scores for sanity;
- write the answer: `open('/root/answer.txt','w').write(str(p1-p2))`.

Conventions and pitfalls:
- **Normalise values.** Map face cards or letters to numbers and strip whitespace. Cast floats like 10.0 to int.
- **Poker-style rules.** Typical tie-break order inside a category is the grouped values ordered by (count, value) descending, then the remaining high values. Handle a low straight (A-2-3-4-5) only if the PDF allows it.
- **Dice or score sums.** Follow the PDF's stated scoring, not intuition.
- **"Matches won" counts matches, not points.** Ties count for neither player.
- **The difference may be negative.** Write it as-is, e.g. `-12`.

**4. Verify.**
- Hand-check 2–3 pairs by printing those rows with their computed scores and comparing against the PDF rules.
- Confirm that p1 + p2 + ties equals the number of pairs.
- Print the distribution of category ranks to make sure every category is reachable and nothing defaults wrongly.
- Run `cat /root/answer.txt`. It must contain only the integer: no text, no units, no trailing explanation.

**Output requirements.** The file is /root/answer.txt, plain text, containing only the number (an integer, sign included if negative).
