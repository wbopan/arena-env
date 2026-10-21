**Tools and setup.** The skills are Python modules. Find them with `find / -name "search_*.py" -not -path "*/proc/*" 2>/dev/null | head`. Then `sys.path.insert(0, <dir of each module>)` and import:
```python
from search_cities import Cities            # Cities().run("Ohio") -> list of Ohio cities
from search_accommodations import Accommodations   # .run(city)
from search_restaurants import Restaurants         # .run(city)
from search_attractions import Attractions         # .run(city)
from search_driving_distance import GoogleDistanceMatrix  # .run(o, d, mode="driving")
```
- `run()` usually returns a pandas DataFrame, or a string if nothing is found. Never print it whole. Use `df.shape`, `df.columns`, and `df.head(3).to_string()`.
- Typical columns (verify them first):
  - Accommodations: `NAME, price, room type, house_rules, minimum nights, maximum occupancy, review rate number, city`
  - Restaurants: `Name, Average Cost, Cuisines, Aggregate Rating, City`
  - Attractions: `Name, Latitude, Longitude, Address, ..., City`
- Driving returns a string like `self-driving, from A to B, duration: X, distance: Y km, cost: Z`. Parse the cost with a regex. If no route exists, it says so or returns no valid cost.
- Do NOT call Flights. No flights are allowed.

**Constraints the evaluator checks (TravelPlanner conventions).**
- **Route.** The trip is a closed loop: Minneapolis → C1 → C2 → C3 → Minneapolis. Use 3 distinct Ohio cities from `Cities().run("Ohio")`.
- **Suggested layout.**
  - Day 1: `from Minneapolis to C1`.
  - Day 3: `from C1 to C2`.
  - Day 5: `from C2 to C3`.
  - Day 7: `from C3 to Minneapolis`.
  - Days 2, 4 and 6 are the plain city name.
  - This gives 2 nights per city.
- **Driving legs.** Every leg must return a valid self-driving result. The Minneapolis↔Ohio legs are long, so check that they exist. If one fails, pick other cities.
- **One mode only.** Use self-driving for every leg. Do not mix taxi with self-driving.
- **Transportation field.**
  - On travel days, write e.g. `"Self-driving: from Minneapolis to Cleveland"`.
  - On stay days, write `"-"`.
- **Meals and attractions.**
  - Each must be a real entry from that day's city. On a travel day, use the destination city (or the origin city for breakfast).
  - Format meals as `"Name, City"`.
  - Never repeat a restaurant or an attraction across the trip.
  - Use `"-"` for meals you skip. Day 1 breakfast and day 7 dinner may be `"-"`.
- **Cuisines.** American, Mediterranean, Chinese and Italian must each appear at least once across all chosen restaurants. Check by substring in `Cuisines`.
- **Attraction format.** `"A;B;"`, ending with `;`. Use at least one per day on stay days.
- **Accommodation.**
  - Use a real `NAME` in the current city, in the format `"NAME, City"`.
  - It must be pet-friendly: `house_rules` must not contain `"No pets"`. Use a case-insensitive check, and treat NaN as OK.
  - `minimum nights` must be ≤ nights stayed (2).
  - `maximum occupancy` should be ≥ 2, or else rooms = ceil(2/occ).
  - Keep the same lodging on both nights in a city.
  - Day 7 accommodation is `"-"`, since you return home.
- **Budget ≤ $5,100.** Compute it as:
  - driving cost for each leg × ceil(2/5) = 1 car
  - plus Σ restaurant Average Cost × 2 people
  - plus Σ nightly price × rooms × 6 nights
  - Pick cheap options when the total is tight. Print the total and assert it is ≤ 5100.

**Step-by-step plan.**
1. Locate the modules. Then run `Cities().run("Ohio")` (print its length and the first 30 entries).
2. For a shortlist of large Ohio cities (e.g. Cleveland, Columbus, Cincinnati, Toledo, Dayton, Akron), test the driving legs Minneapolis→X and X→Minneapolis, plus the legs between cities. Check that each city has pet-friendly lodging with min nights ≤ 2. Print only counts and costs.
3. Write one script, `/app/build.py`, that:
   1. picks the 3 cities and their order;
   2. filters lodging to pet-friendly, min nights ≤ 2 and occupancy ≥ 2, then takes the cheapest;
   3. greedily assigns restaurants with no reuse, first forcing one of each required cuisine, then the cheapest remaining;
   4. assigns 1–2 unused attractions per day;
   5. computes the budget;
   6. writes the JSON.
4. Output goes to `/app/output/itinerary.json`. Run `os.makedirs("/app/output", exist_ok=True)` first. Use `json.dump(..., indent=2)`.
5. Validate with a one-liner:
   - `plan` has exactly 7 objects with `day` 1..7.
   - Every object has the keys `day, current_city, transportation, breakfast, lunch, dinner, attraction, accommodation`, all strings except `day`.
   - Attractions end with `;`.
   - No string contains "Flight".
   - There are no duplicate restaurants.
   - All 4 cuisines are covered.
   - The budget is printed.

**Output format.**
- Top-level keys are `plan` (7 day objects) and `tool_called`.
- `tool_called` lists the skills actually used, e.g. `["search_cities","search_driving_distance","search_accommodations","search_restaurants","search_attractions"]`.
- Never include `search_flights` in `tool_called`.
- `current_city` is `"from A to B"` on moving days.
