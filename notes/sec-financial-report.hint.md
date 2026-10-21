1. Find the skill scripts (`find / -name search_fund.py`) and `ls` the TSVs in /root/2025-q2 and /root/2025-q3.
2. Run `search_fund.py` to get accession numbers (Renaissance q3; Berkshire Hathaway Inc q2 and q3), then `one_fund_analysis.py` for AUM, stock count, and the Q2→Q3 increases (top 5 CUSIPs by dollar increase).
3. Run `search_stock_cusip.py palantir`, then `holding_analysis.py --quarter 2025-q3 --topk 3` and copy the manager names exactly.
4. Write /root/answers.json (numbers as numbers, lists of strings), then json.load it to verify the keys and types.
