## Reference notes

- Read the **entire** scoring-rules PDF before coding the score function. Use `pypdf`:
  ```python
  from pypdf import PdfReader
  reader = PdfReader("/root/work/background.pdf")
  for i, page in enumerate(reader.pages, 1):
      print(f"--- Page {i} ---\n{page.extract_text()}")
  ```
  Check the exact score assigned to each three-die throw, including special combinations, rule precedence, and whether any scores are compared as categories rather than ordinary totals. Do not assume the score is the sum of the dice.

- Read the named Excel sheet with `pandas`:
  ```python
  import pandas as pd
  df = pd.read_excel("/root/work/data.xlsx", sheet_name="Games")
  print(df.columns.tolist(), df.shape, df.head())
  ```
  Confirm the four column names and convert `Game`, `Die1`, `Die2`, `Die3` to integers as needed. Rows are **not** in game-number order: index scores by `Game`, not by row position.

- Pair game numbers `2*k-1` (Player 1) and `2*k` (Player 2). Apply the PDF’s scoring rules independently to each row, then compare the two scores using its match rules. Count `<`, `>`, and `==` outcomes; `difference = player1_wins - player2_wins`. Check that game numbers are unique and every odd game has its corresponding even game.

- Write a plain JSON object, not an Excel file. `json.dump(result, file)` from the standard library writes the required fields; ensure their values are Python `int` (not NumPy integer types). Reopen the JSON and check the field names, integer types, and that wins plus ties equals the number of pairs.
