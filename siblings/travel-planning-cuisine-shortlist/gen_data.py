import csv
import random

random.seed(4242)

STATES = {
    "Ohio": ["Cleveland", "Columbus", "Cincinnati", "Toledo", "Akron", "Dayton"],
    "Indiana": ["Indianapolis", "Fort Wayne", "Evansville"],
    "Michigan": ["Detroit", "Grand Rapids", "Lansing"],
}
pairs = [(s, c) for s, cs in STATES.items() for c in cs]
random.shuffle(pairs)
with open("cities.txt", "w") as f:
    for s, c in pairs:
        f.write(f"{s}\t{c}\n")

CUISINES = ["American", "Chinese", "Italian", "Mediterranean", "Pizza", "Cafe", "Bakery",
            "Seafood", "Indian", "Mexican", "Fast Food", "Desserts", "Mediterranean Fusion",
            "Pan-Asian", "Italian-American"]
ADJ = ["Golden", "Rusty", "Blue", "Silver", "Hungry", "Happy", "Little", "Grand", "Olive",
       "Red", "Green", "Copper", "Lucky", "Old", "Urban", "Smoky", "Crimson", "Twin",
       "Wild", "Velvet", "Iron", "Salty", "Sweet", "Bold"]
NOUN = ["Spoon", "Fork", "Lantern", "Kitchen", "Table", "Garden", "Oven", "Bistro", "Wok",
        "Grill", "Plate", "Harbor", "Pantry", "Tavern", "Diner", "Corner", "Ladle", "Basil",
        "Barrel", "Hearth"]
RATINGS = [2.9, 3.4, 3.6, 3.9, 4.1, 4.1, 4.3, 4.5, 4.8]

used = set()
rows = []
for s, c in pairs:
    for _ in range(14):
        while True:
            name = f"The {random.choice(ADJ)} {random.choice(NOUN)}"
            if name not in used:
                used.add(name)
                break
        cu = random.sample(CUISINES, random.randint(1, 4))
        if c == "Dayton":
            cu = [x for x in cu if x != "Mediterranean"] or ["Cafe"]
        rows.append([name, random.randint(8, 95), ", ".join(cu), random.choice(RATINGS), c])
random.shuffle(rows)
with open("restaurants.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Name", "Average Cost", "Cuisines", "Aggregate Rating", "City"])
    w.writerows(rows)
