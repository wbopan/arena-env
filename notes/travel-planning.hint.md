1. Find the `search_*.py` modules, import them via `sys.path`, and inspect DataFrame columns and shape only, never full prints.
2. Pick 3 Ohio cities (from `Cities().run("Ohio")`) where every self-driving leg from and back to Minneapolis is valid. Use the loop Minneapolis→C1(d1)→C2(d3)→C3(d5)→Minneapolis(d7).
3. In one script:
   - choose pet-friendly lodging (no "No pets", min nights ≤ 2, occupancy ≥ 2);
   - use unique restaurants covering American, Mediterranean, Chinese and Italian;
   - use unique attractions, each list ending with `;`;
   - keep the total ≤ $5,100;
   - use no flights.
4. Write `/app/output/itinerary.json` with 7 day objects plus `tool_called`. Re-load it and assert the keys, day count and budget.
