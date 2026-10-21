# Cheapest pet-friendly Ohio road trip

Inputs in `/root/work`:

- `cities.txt`: one city per line, formatted `State<TAB>City`.
- `accommodations.csv`: columns `NAME`, `price` (USD per night for the whole listing), `room type`, `house_rules` (rules joined with ` && `), `minimum nights`, `maximum occupancy`, `city`.
- `distance.csv`: directed self-driving legs. Columns `origin`, `destination`, `duration`, `distance_km`, `cost` (USD per car for that leg).

Two travelers with a dog share one car. They leave Minneapolis, visit exactly 3 distinct cities in Ohio (as listed in `cities.txt`), stay exactly 2 nights in each, and drive back to Minneapolis. The route is Minneapolis -> A -> B -> C -> Minneapolis.

A leg can be driven only if that exact (origin, destination) row exists in `distance.csv`. Each leg's `cost` is counted once.

In each visited city they book one listing located in that city. The listing must meet all of these conditions:

- It is pet-friendly, meaning `house_rules` does not contain `No pets`.
- Its `maximum occupancy` is at least 2.
- Its `minimum nights` is at most 2.

The cost of a listing is `price` x 2.

Find a plan that minimizes total cost, where total cost = driving cost + accommodation cost.

Write `/root/work/trip.json` in this form:

```json
{"route": ["Minneapolis", "A", "B", "C", "Minneapolis"],
 "accommodations": ["<NAME in A>", "<NAME in B>", "<NAME in C>"],
 "driving_cost": 0, "accommodation_cost": 0, "total_cost": 0}
```

- Accommodation names must match `NAME` exactly and be listed in route order.
- Costs are in USD with no rounding.
- If several plans tie for the minimum, any one of them is acceptable.
