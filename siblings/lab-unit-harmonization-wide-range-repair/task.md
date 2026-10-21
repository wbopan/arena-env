# Harmonize a wide multi-site lab panel

`/root/work/labs_wide.csv` has one row per patient. The first column is `patient_id`, followed by 7 lab columns merged from several hospitals.

`/root/work/lab_reference.csv` has one row per lab column with these fields:
- `feature`: the lab column name.
- `min`, `max`: the inclusive expected physiological range in US conventional units.
- `unit`: the conventional unit.
- `alt_factors`: semicolon-separated multiplicative factors. Each factor converts a value in an alternative unit into the conventional unit. Factors are listed in the order they must be tried.

Raw cells may contain any of the following:
- Leading or trailing whitespace.
- Scientific notation, such as `1.2340e+02`.
- A comma as the decimal separator. `12,34` means 12.34. Commas are never thousands separators.

Missing values appear as empty cells, `NA` or `NaN`.

Steps:
1. Drop every patient row that has any missing lab value.
2. Parse each remaining value to a number.
3. If the value lies within [min, max], keep it. Otherwise, multiply it by each alt factor in the listed order. Keep the first product that lies within [min, max]. If no product does, keep the original value.
4. Format each lab value with exactly two decimals (`X.XX`). Do not use thousands separators, scientific notation or padding.

Output: write `/root/work/harmonized.csv`.
- It must be comma-separated.
- It must have the same header and column order as the input.
- `patient_id` values must be unchanged.
- The surviving rows must stay in their original order.
