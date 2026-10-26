# Industrial Zone Sites from a SQLite Map

For each city in `/root/work/industry.sqlite`, find its highest-adjacency Industrial Zone site. The database contains `Cities(city_id, x, y)`, `Tiles(tile_id, x, y, terrain, resource, improvement)`, and `Built(city_id, district, tile_id)`. `tile_id` links built districts to tiles. Coordinates use Civ6 odd-r hexes: odd rows shift right. Convert `(x, y)` to cube coordinates `(x - (y - (y & 1)) // 2, -x + (y - (y & 1)) // 2 - y, y)`; hex distance is half the sum of absolute cube-coordinate differences.

A site is eligible when it is within distance 2 of its city center, is not the center or any tile in `Built`, has `terrain` other than `MOUNTAIN`, and has `resource` other than `IRON`. Each city has at least one eligible site. Evaluate each site against the unchanged map; the selected Industrial Zones are hypothetical and do not affect one another.

For each adjacent tile (distance 1), award +2 if it contains a built `AQUEDUCT`, and +1 if its improvement is `QUARRY`. Also award +1 per complete pair of adjacent `MINE` improvements, separately +1 per complete pair of adjacent `LUMBER_MILL` improvements, and +1 per complete pair of adjacent district tiles. For this last count, city centers and tiles in `Built` count; do not count the hypothetical Industrial Zone itself. The categories are floored separately.

Choose each city's highest score, breaking ties by smaller site `y`, then `x`. Write `/root/work/industry_answer.csv` with header `city_id,x,y,bonus`, one row per city in ascending `city_id` order. All fields are integers; `bonus` has no units or rounding.
