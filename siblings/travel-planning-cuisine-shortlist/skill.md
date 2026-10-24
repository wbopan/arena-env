## Reference notes

Use the supplied files directly with Python’s standard-library `csv` module. The `search_restaurants` skill offers `Restaurants().run(city)`, but direct CSV reading is better here because the task requires specific filtering and tie-breaking across the supplied data.

- Read `cities.txt` line by line; split each line on `"\t"` into state and city. Keep Ohio cities, then sort their names.
- Read `restaurants.csv` with `csv.DictReader` and `encoding="utf-8"`. Match `City` exactly. For cuisine membership, use `row["Cuisines"].split(", ")`; substring checks would incorrectly match names such as `Italian-American`.
- Convert `Average Cost` to `int` and `Aggregate Rating` to `float`. Keep costs `<= 60`. Select by the key `(-rating, cost, name)` in ascending order: highest rating, then lowest cost, then plain ascending name.
- For each city and each cuisine in sorted order, emit a row even if no restaurant qualifies. Use `"-"`, `0`, and `"0.0"` for missing options.
- Write with `csv.writer`, `newline=""`, and the exact header `city,cuisine,restaurant,average_cost,aggregate_rating`. Format ratings with `f"{rating:.1f}"` so every output rating has one decimal place.

A compact workflow: inspect the input headers and a few lines, write one Python script to read/filter/select/write, run it, then inspect the output header, row ordering, and representative rows.
