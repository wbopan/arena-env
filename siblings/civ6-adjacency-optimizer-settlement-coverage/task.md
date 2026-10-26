# Settlement Coverage on an Odd-Row Hex Map

Choose one city center from the candidate tiles in `/root/work/settlement.json`. The file contains `width`, `height`, a `tiles` array, and a `candidates` array of `[x, y]` coordinates. Every tile has integer `x`, `y`, and `weight` fields. The weight represents the value of having that tile within the city's working area; it is not a district adjacency bonus.

A city works every map tile at hex distance at most 2 from its center, including the center tile. Use Civ6 odd-r offset coordinates: odd-numbered rows are shifted right. To calculate distance, convert `(x, y)` to cube coordinates `(x - (y - (y & 1)) // 2, -x + (y - (y & 1)) // 2 - y, y)`; hex distance is half the sum of the three absolute cube-coordinate differences.

For each candidate, sum the weights of its worked tiles. Select the candidate with the greatest sum. Break ties by smaller `y`, then smaller `x`. Write exactly one JSON object to `/root/work/settlement_answer.json` with fields `center` (`[x, y]`), `value` (integer sum), and `worked_count` (integer number of map tiles within range). Count zero-weight tiles too. Do not count positions outside the map.
