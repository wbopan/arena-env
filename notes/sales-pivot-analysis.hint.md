1. Inspect cheaply: the PDF with a pdfplumber one-liner (page count, first and last table rows), and income.xlsx with a pandas one-liner (columns, head(2)); identify the join key (SA2).
2. In one script: extract all PDF pages (strip commas, convert to numeric), merge with income, then add `Quarter=pd.qcut(MEDIAN_INCOME,4,labels=Q1..Q4)` and `Total=EARNERS*MEDIAN_INCOME`.
3. Write "SourceData" with openpyxl, then add 4 pivot sheets ("Population by State", "Earners by State", "Regions by State", "State Income Quartile" with Quarter as axisCol). All pivots use cacheId=0 and full cacheFields/pivotFields lists.
4. Save to /root/demographic_analysis.xlsx, then reload to verify sheet names, `_pivots`, field indices and subtotals, Quarter labels, Total, and row counts.
