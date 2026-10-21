1. With openpyxl, list sheets, headers and every "???" coordinate, along with their row/column labels; print only those rows, not whole sheets.
2. Find the links: totals = sum of parts, YoY % = (cur/prev−1)×100, share = part/total×100, CAGR = ((end/start)^(1/n)−1)×100. Solve in dependency order, preferring raw sums over rounded percentages.
3. Write plain numbers (not formulas, not strings), rounded like the neighbouring cells, and save as `nasa_budget_recovered.xlsx`.
4. Reload the output, assert no "???" remains, and re-check all sum, YoY, share and CAGR constraints.
