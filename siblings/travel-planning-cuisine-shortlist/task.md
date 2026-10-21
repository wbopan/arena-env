# Cuisine shortlist for Ohio cities

Inputs in `/root/work`:

- `cities.txt`: one city per line, formatted `State<TAB>City`.
- `restaurants.csv`: columns `Name`, `Average Cost` (USD per person, integer), `Cuisines` (entries separated by `, `), `Aggregate Rating` (one decimal), `City`.

Compute one result for every city of the state **Ohio** listed in `cities.txt`, crossed with each of these cuisines: `American`, `Chinese`, `Italian`, `Mediterranean`.

A restaurant qualifies for a (city, cuisine) pair when all of these hold:

- Its `City` equals the city.
- Its `Cuisines` list contains the cuisine as an exact entry. For example, `Mediterranean Fusion` or `Italian-American` do not count as `Mediterranean` or `Italian`.
- Its `Average Cost` is at most 60.

Among the qualifying restaurants, pick the one with the highest `Aggregate Rating`. Break ties by lower `Average Cost`, then by `Name` in plain ascending string order.

Write `/root/work/meal_options.csv`:

- Header: exactly `city,cuisine,restaurant,average_cost,aggregate_rating`.
- One row per (city, cuisine) pair.
- Rows sorted by city alphabetically, then by cuisine alphabetically.
- `restaurant` is the exact `Name`.
- `average_cost` is an integer.
- `aggregate_rating` has one decimal place.
- If no restaurant qualifies for a pair, write `-` as the restaurant, `0` as the average cost and `0.0` as the rating.
