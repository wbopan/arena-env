# Diverse attraction picks

Choose one attraction in each city for a three-city sightseeing itinerary. The inputs are `/root/work/visit.json` and `/root/work/attractions.csv`. `visit.json` gives an ordered `cities` array and a `budget_usd` for all admissions combined. The CSV has columns `Name`, `City`, `Category`, `AdmissionUSD`, and `Score`. Admission is the price in whole US dollars for the entire traveling party; Score is an integer preference score. Names identify attractions uniquely.

Select exactly one CSV attraction for each city, in the order specified by `visit.json`. The selected attractions must have three different categories, and their combined admission must not exceed the budget. Among feasible selections, maximize the sum of Scores. If several selections have the same score, choose the one with the lowest combined admission. If there is still a tie, choose the lexicographically smallest tuple of attraction names in city order. No other attractions should appear in the result.

Write exactly one file, `/root/work/sights.json`. It must contain `selected`, an array of objects in city order with fields `city`, `attraction`, `category`, `admission_usd`, and `score`, plus integer fields `total_admission_usd` and `total_score`. Use the exact capitalization of names, cities, and categories in the input.
