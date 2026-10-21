# IPF GL Points for a Meet

The workbook `/root/work/meet.xlsx` has a sheet `Results` with one row per lifter. Its columns are:

- Name
- Sex (M, F, Mx)
- Equipment (Raw, Wraps, Single-ply, Multi-ply)
- Event (SBD = full powerlifting, B = bench-only)
- BodyweightKg, Best3SquatKg, Best3BenchKg, Best3DeadliftKg

An empty or negative best lift means the lift was failed or not taken.

Compute IPF GOODLIFT (GL) points for every lifter:

- **TotalKg for SBD:** squat + bench + deadlift. It is 0 if any of the three is empty or <= 0.
- **TotalKg for B:** the bench value. It is 0 if the bench is empty or <= 0.
- **Parameter selection:** Sex Mx uses the M parameters. Raw and Wraps use the Raw parameters. Single-ply and Multi-ply use the Equipped parameters.
- **GL formula:** GL = TotalKg * max(0, 100 / (A - B * exp(-C * BodyweightKg))).
- **Zero cases:** GL is 0 when BodyweightKg < 35 or TotalKg is 0.

Parameters (A, B, C):

| Event | Sex | Equip | A | B | C |
|---|---|---|---|---|---|
| SBD | M | Raw | 1199.72839 | 1025.18162 | 0.009210 |
| SBD | M | Equipped | 1236.25115 | 1449.21864 | 0.01644 |
| SBD | F | Raw | 610.32796 | 1045.59282 | 0.03048 |
| SBD | F | Equipped | 758.63878 | 949.31382 | 0.02435 |
| B | M | Raw | 320.98041 | 281.40258 | 0.01008 |
| B | M | Equipped | 381.22073 | 733.79378 | 0.02398 |
| B | F | Raw | 142.40398 | 442.52671 | 0.04724 |
| B | F | Equipped | 221.82209 | 357.00377 | 0.02937 |

Write `/root/work/gl_points.csv` with this exact header:

`Name,Event,TotalKg,GLPoints`

Format requirements:

- One row per lifter.
- TotalKg rounded to 1 decimal.
- GLPoints rounded to 2 decimals.
- Rows sorted by GLPoints descending; break ties by Name ascending.
