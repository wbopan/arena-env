1. Inspect the header, shape and missing counts via a pandas one-liner (`read_csv(dtype=str)`), and peek at `ckd_feature_descriptions.csv`.
2. Write one script that:
   - drops rows with any missing value;
   - parses sci-notation and `,`-decimals to float;
   - for out-of-range values, tries the per-feature US-unit factors (e.g. creatinine ×0.0113, Hb ×0.1/×1.611, Ca ×4/×2, Mg ×2.43/×1.215, lipids ×38.67, glucose ×18.02, kPa ×7.5) and keeps the first in-range result, with a 5% tolerance clamp.
3. Format every value with `f"{x:.2f}"` and save to `/root/ckd_lab_data_harmonized.csv` (62 columns, `index=False`).
4. Validate: regex `^-?\d+\.\d{2}$`, no `e` or `,`, and zero out-of-range values per column.
