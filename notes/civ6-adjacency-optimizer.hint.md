1. Read `/data/scenario_3/scenario.json`, then explore the `.Civ6Map` SQLite schema (Plots/PlotFeatures/PlotResources/rivers) with LIMIT queries. Locate civ6lib (`find / -name "civ6lib*"`) and use its PlacementRules and AdjacencyCalculator.
2. Write one Python script that enumerates valid city centers and searches district placements. Respect: within 3 tiles, at most `1+(pop-1)//3` specialty districts, free Aqueduct/Dam/Neighborhood, odd-r hex neighbours, each +0.5 category floored separately, and woods/rainforest/bonus resources destroyed under districts.
3. Write `/output/scenario_3.json` in the exact single- or multi-city format, with integer bonuses summing to `total_adjacency`.
4. Re-validate every placement and recompute the adjacency from the saved file before finishing.
