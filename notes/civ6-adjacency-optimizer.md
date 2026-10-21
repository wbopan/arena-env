**Inputs and tools**
- Read `/data/scenario_3/scenario.json` with `python3 -c "import json;print(json.load(open('/data/scenario_3/scenario.json')))"`. It gives `map_file`, `num_cities`, `population` and `civilization`.
- The `.Civ6Map` file is a SQLite database. Use Python's `sqlite3`.
  - Start with `SELECT name FROM sqlite_master WHERE type='table'`.
  - Then run `PRAGMA table_info(T)` and `SELECT * FROM T LIMIT 3` on the map-related tables only. Expect something like `Map` (Width/Height), `Plots` (ID, TerrainType, maybe river flags), `PlotFeatures`, `PlotResources`, `PlotRivers`, and possibly `PlotImprovements`.
  - Convert IDs to coordinates with `x = id % width`, `y = id // width`.
  - Never dump whole tables. Use `COUNT(*)`, `DISTINCT` and `LIMIT`.
- Check whether the skill library is importable before writing your own rules: `find / -name "civ6lib*" -o -name hex_utils.py 2>/dev/null | head`.
  - If it is present, use it:
    ```python
    from civ6lib import DistrictType, Tile, get_placement_rules, get_adjacency_calculator, validate_district_count, validate_district_uniqueness
    rules = get_placement_rules(tiles, city_center=(x, y), population=pop)
    rules.validate_placement(DistrictType.CAMPUS, x, y, existing).valid
    total, per = get_adjacency_calculator(tiles).calculate_total_adjacency(placements)
    ```
  - Inspect the `Tile` fields and the function signatures with `grep -n "def \|class \|:" file | head -60`. Also check whether the library ships a map parser. Using its calculator ensures your numbers match the grader's.

**Hex grid (odd-r offset; odd rows shifted right)**
- Neighbours:
  - Even row (y%2==0): `[(1,0),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1)]`
  - Odd row: `[(1,0),(1,-1),(0,-1),(-1,0),(0,1),(1,1)]`
- Distance:
  ```python
  def cube(c, r):
      x = c - (r - (r & 1)) // 2
      return x, -x - r, r
  d = sum(abs(a - b) for a, b in zip(cube(x1, y1), cube(x2, y2))) // 2
  ```

**City rules**
- A city center cannot be placed on water (coast, ocean, lake), a mountain, or a natural wonder.
- With multiple cities:
  - Same landmass: distance ≥ 4.
  - Different landmasses: distance ≥ 3.
- A city center on a geothermal fissure or a luxury/strategic resource keeps that feature. It still gives adjacency to nearby districts.

**District placement rules**
- The tile must be within 3 of its city center.
- It must not be a mountain, a natural wonder, a strategic resource (Iron, Horses, Niter, Coal, Oil, Aluminum, Uranium) or a luxury resource.
- It must not be occupied (the city center counts as occupied).
- Bonus resources, woods, rainforest and marsh are allowed, but placing a district destroys them.
- Type-specific rules:
  - Harbor and Water Park: on Coast or Lake, adjacent to land.
  - Aerodrome and Spaceport: flat land.
  - Encampment and Preserve: not adjacent to the city center.
  - Aqueduct: adjacent to the city center AND to fresh water (mountain, river, lake or oasis).
  - Dam: on floodplains, with the river crossing at least 2 edges.

**District limits**
- Specialty districts per city: `1 + (pop-1)//3`. This gives 1 for pop 1–3, 2 for 4–6, 3 for 7–9 and 4 for 10–12.
- These do NOT count toward the limit: Aqueduct/Bath, Neighborhood/Mbanza, Canal, Dam, Spaceport.
  - They are free and each one counts as a "district" for the +0.5 bonus.
  - Aqueduct, Dam and Canal also give an Industrial Zone +2.
- Uniqueness:
  - One per city: Campus, Holy Site, Theater, Commercial Hub, Harbor, Industrial Zone, Entertainment Complex, Water Park, Encampment, Aerodrome, Preserve.
  - One per civilization: Government Plaza, Diplomatic Quarter.
- Placements are a dict keyed by district type, so each type appears once in the output.

**Adjacency formulas**
- Bonuses with the same source category stack; the +0.5 rules are handled below.
- Campus: +2 per geothermal fissure, +2 per reef, +1 per mountain, +0.5 per rainforest, +0.5 per district.
- Holy Site: +2 per natural wonder, +1 per mountain, +0.5 per woods, +0.5 per district.
- Theater Square: +2 per built wonder, +2 per Entertainment Complex, +2 per Water Park, +0.5 per district.
- Commercial Hub:
  - +2 once if its own tile is on a river (any river edge; binary).
  - +2 per adjacent Harbor.
  - +0.5 per district.
- Harbor: +2 per adjacent city center, +1 per coastal resource (Fish, Crabs, Whales, Pearls), +0.5 per district.
- Industrial Zone:
  - +2 per Aqueduct, Dam or Canal.
  - +1 per Quarry or strategic resource.
  - +0.5 per Mine, +0.5 per Lumber Mill, +0.5 per district.
- Government Plaza gives +1 to each adjacent specialty district (Campus, Holy Site, Theater, Commercial Hub, Harbor, Industrial Zone). It also counts as a district for the +0.5 bonus.
- These have no adjacency of their own (bonus = 0): Entertainment Complex, Water Park, Encampment, Aerodrome, Spaceport, Government Plaza, Preserve.

**Pitfalls**
- **Floor each +0.5 category separately, then sum.** For example, 1 mine, 1 lumber mill and 1 district gives 0, not 1. In code: `floor(n_district/2) + floor(n_rainforest/2) + ...`.
- **Districts that count for "+0.5 per district":** all of the ones listed above, plus City Center, Aqueduct, Dam, Canal and Neighborhood. Count city centers of every city, not only the district's own.
- **Feature destruction:** woods, rainforest, marsh and bonus resources under ANY placed district disappear. A Campus loses rainforest bonus from a tile that is now a district, though that tile then counts as a district instead. Mountains, reefs, fissures and strategic/luxury resources are never destroyed, because districts cannot be placed on them (except reef, which is water).
- **Reef and Geothermal:** both are features. Find their exact names with `SELECT DISTINCT FeatureType FROM PlotFeatures`. Natural wonders also appear as features.
- **Map improvements:** if there is no improvements table, mines, quarries and lumber mills are 0.
- **Civilization field:** standard rules apply unless the library implements civilization-specific behaviour. Grep civ6lib for the civilization name.
- **River detection:** a tile is "on a river" if any of its edges has a river. Edges are stored on one tile (e.g. IsWOfRiver/IsNWOfRiver/IsNEOfRiver flags or a `PlotRivers` table), so neighbouring tiles' flags must be checked as well. Check how civ6lib builds `Tile.river` and mirror that.

**Plan (about 10–15 commands)**
1. `cat` the scenario JSON. Locate civ6lib and hex_utils and grep their APIs.
2. Inspect the SQLite schema, row counts and DISTINCT terrain, feature and resource values.
3. Write `/tmp/solve.py`:
   - Parse the tiles.
   - Enumerate every valid city center. For multiple cities, enumerate valid center pairs/sets, pruned to centers near high-value features (mountains, reefs, fissures, rivers, coast resources).
   - For each center, list the valid tiles within 3.
   - Search assignments of up to N specialty districts, plus free districts (Aqueduct, Dam, Canal, Neighborhood) that raise others via the +0.5 district bonus and the Industrial Zone +2.
   - Use greedy or beam search plus local swaps. Exhaustive search is fine if the candidate set is small.
   - Score with the library calculator, or your exact reimplementation, after applying destruction effects.
   - Validate every placement with `rules.validate_placement`, district counts and uniqueness.
4. Write the JSON. Re-load it, recompute the adjacency independently, and assert that `sum(adjacency_bonuses) == total_adjacency`.
   - Coordinates must be `[x, y]` integer lists.
   - Use exact district enum names (`CAMPUS`, `COMMERCIAL_HUB`, `INDUSTRIAL_ZONE`, ...).
   - Bonuses must be integers.
   - Include every placed district, with a 0 bonus where it has none.

**Output: `/output/scenario_3.json`** (run `mkdir -p /output` first)
- Single city:
  ```json
  {"city_center":[x,y],"placements":{"CAMPUS":[x,y],...},"adjacency_bonuses":{"CAMPUS":3,...},"total_adjacency":N}
  ```
- Multiple cities: replace `city_center` with `"cities":[{"center":[x1,y1]},{"center":[x2,y2]}]`. The number of centers must equal `num_cities`.
- Any invalid placement, or a bonus total that doesn't match, scores 0.
