# Dots Team Competition Standings

The file `/root/work/lifters.csv` lists the lifters of a team meet. Its columns are:

- Name (unique)
- Team
- Sex (M, F, Mx)
- BodyweightKg, Best3SquatKg, Best3BenchKg, Best3DeadliftKg

An empty or negative lift means the lift was failed.

Compute each lifter's Dots points:

- **TotalKg:** squat + bench + deadlift. If any of the three lifts is empty or <= 0, the lifter bombed out and their Dots is 0.
- **Dots formula:** Dots = TotalKg * 500 / (A*x^4 + B*x^3 + C*x^2 + D*x + E), where x is BodyweightKg clamped to the sex-specific range.
- **Men (M and Mx):** A=-0.0000010930, B=0.0007391293, C=-0.1918759221, D=24.0900756, E=-307.75076. Clamp x to [40, 210].
- **Women (F):** A=-0.0000010706, B=0.0005158568, C=-0.1126655495, D=13.6175032, E=-57.96288. Clamp x to [40, 150].

Scoring:

- A team's score is the sum of the unrounded Dots of its 3 highest-scoring members.
- Teams are ranked by score, highest first; rank 1 is the best team.

Write `/root/work/team_standings.json` as a JSON array with one object per team, ordered by rank. Each object has exactly these keys:

- `rank` (integer, starting at 1)
- `team` (string)
- `score` (number rounded to 2 decimals)
- `top_lifters` (list of the 3 counted member names, ordered by Dots descending)
