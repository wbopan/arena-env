1. `cat math-model.md`, then summarize `/root/network.json` with a json.load one-liner (sizes, gencost format, reserve fields). Never print the file.
2. Write one CasADi/IPOPT script: vectorized SX pi-model flows (tap 0 → 1, shift in degrees, bc/2 at each end), sparse incidence matrices for nodal balance, rateA² limits, slack Va = 0, and cost in MW.
3. Recompute flows, mismatches and violations in numpy and write `/root/report.json` in the exact schema, with plain floats and the top branches sorted by loading_pct.
4. Run in the background (nohup) and tail the log, then verify the report's summary, feasibility_check and list lengths with a one-liner.
