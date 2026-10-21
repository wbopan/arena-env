1. Grep `/root/data/data-readme.md` and print the Data headers and a few rows (openpyxl) to find Name, Sex, BodyweightKg and the Best3 Squat/Bench/Deadlift columns.
2. With openpyxl, copy those columns in Data order to sheet "Dots", then add `TotalKg` = `=ROUND(SUM(squat:deadlift),3)` and `Dots` = `ROUND(Total*500/poly4(clamped BW),3)`.
3. Dots coefficients: men/Mx A..E = -1.093e-6, 7.391293e-4, -0.1918759221, 24.0900756, -307.75076 with BW clamped to 40–210. Women = -1.0706e-6, 5.158568e-4, -0.1126655495, 13.6175032, -57.96288 with BW clamped to 40–150. Return 0 if BW or total is 0.
4. Save in place, run `recalc.py` (find it), confirm 0 errors, and spot-check the values against a Python recomputation.
