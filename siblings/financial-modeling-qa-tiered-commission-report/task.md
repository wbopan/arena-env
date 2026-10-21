A broker needs a per-client report of trading charges.

Inputs:
- /root/work/data.xlsx contains sheet `Trades` with columns `trade_id`, `client`, `side` (BUY or SELL), `quantity`, and `price` (USD).
- /root/work/background.pdf contains the firm's commission schedule. It defines the notional tiers and rates, the minimum commission, and an extra regulatory fee that applies to SELL trades.

Task:
1. For every trade, compute notional = quantity x price, rounded to cents.
2. Find the tier that contains the notional. That tier's rate applies to the entire notional, so this is not a marginal schedule. Tier lower bounds are inclusive.
3. Apply the minimum commission as described in the PDF.
4. Add the regulatory fee if the trade is a SELL.
5. Round each trade's total charge (commission + regulatory fee) to 2 decimals.
6. Sum the rounded charges per client.

Output: write /root/work/commissions.csv. Use a header row `client,trades,total_charges` followed by one row per client, sorted alphabetically by client:
- `trades`: the integer count of that client's trades
- `total_charges`: the sum of the rounded per-trade charges in USD, written with exactly 2 decimals and no thousands separators or currency symbols
