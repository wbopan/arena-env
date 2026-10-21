1. Use openpyxl to print non-empty cells of "Task" (rows 1–55, cols A–N) and of "Data" (rows 1–45). Find the codes column, the year header row and type, the block labels (X/M/GDP), the stats-row labels and the H35 number format.
2. In one script, fill H12:L31 with `=INDEX(Data!rng,MATCH($D12,Data!codes,0),MATCH(H$10,Data!years,0))`. Fill H35:L40 with `=(X-M)/GDP` (×100 unless the format is %). Add MIN/MAX/MEDIAN/AVERAGE/PERCENTILE 0.25/0.75 and `=SUMPRODUCT(H35:H40,H26:H31)/SUM(H26:H31)`.
3. Save in place to gdp.xlsx with formulas only and no style changes.
4. Run `python recalc.py gdp.xlsx 60` and confirm 0 errors. Then spot-check the values with `data_only=True`, without saving.
