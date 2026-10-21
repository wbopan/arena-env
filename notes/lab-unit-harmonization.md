**Goal:** read `/root/environment/data/ckd_lab_data.csv`, which has 62 columns (lab features, possibly plus ID columns). Write `/root/ckd_lab_data_harmonized.csv` with these properties:
- The same columns, in the same order.
- Every row with any missing value removed.
- Every numeric value parsed from sci-notation or comma decimals, converted to US conventional units when it lies outside the physiological range, and formatted `f"{x:.2f}"`.
- No `e`, no `,` decimal separators, exactly 2 decimals.

**Inspect cheaply (do not cat whole files):**
- `head -c 600 /root/environment/data/ckd_lab_data.csv`
- `wc -l` on the input.
- `python3 -c "import pandas as pd;d=pd.read_csv('...ckd_lab_data.csv',dtype=str);print(d.shape);print(list(d.columns));print(d.isna().sum().sum())"`
- `head -5` of `ckd_feature_descriptions.csv`.

Identify non-lab columns (e.g. a patient ID). Keep them unchanged and do not format them.

**Reading:** use `pd.read_csv(path, dtype=str)`. This keeps raw strings, so `12,34` survives. If the file uses commas inside quoted fields, pandas handles that; check `shape[1]==62`.

**Missing rows:** a cell counts as missing if it is NaN, or if its stripped lowercase value is in `{'', 'nan', 'none', 'null'}`. Drop any row with at least one missing lab value (`df[mask].reset_index(drop=True)`).

**Parsing each value:**
1. Strip whitespace.
2. If the value contains `e`/`E`, try `float(s)`.
3. If it contains both `,` and `.`, remove the commas (thousands separator).
4. Otherwise replace `,` with `.`.
5. Call `float()`.

**Unit conversion (range-based):**
- If `lo <= v <= hi`, keep `v`.
- Otherwise try each factor `f` in the list below; return the first `v*f` that lands in `[lo, hi]`.
- If no factor works, allow a 5% tolerance around the bounds and clamp to the nearest bound when within it.
- Otherwise leave the value unchanged and report it.
- Never clamp aggressively.

**Ranges and factors.** Format is `[lo, hi]` in US units, followed by the multiplier(s) that convert the alternative unit to US. "none" means the unit is the same in SI.

- **Kidney function**
  - Serum_Creatinine [0.2, 20]: ×0.0113 (µmol/L)
  - BUN [5, 200]: ×2.8 (mmol/L urea)
  - eGFR [0, 150]: none
  - Cystatin_C [0.4, 10]: none
  - BUN_Creatinine_Ratio [5, 50]: none
- **Electrolytes** (mEq = mmol, so none convert)
  - Sodium [110, 170]
  - Potassium [2, 8.5]
  - Chloride [70, 140]
  - Bicarbonate [5, 40]
  - Anion_Gap [0, 40]
  - Magnesium [0.5, 10]: ×2.43 (mmol/L), ×1.215 (mEq/L)
- **Mineral and bone**
  - Serum_Calcium [5, 15]: ×4.0 (mmol/L), ×2.0 (mEq/L)
  - Ionized_Calcium [0.8, 2.0] in mmol/L: ×0.25 (from mg/dL)
  - Phosphorus [1, 15]: ×3.1
  - Intact_PTH [5, 2500]: ×9.43 (pmol/L)
  - Vitamin_D_25OH [4, 200]: ×0.4 (nmol/L)
  - Vitamin_D_1_25OH [5, 100]: ×0.385 (pmol/L)
  - Alkaline_Phosphatase [20, 2000]: none
- **Hematology/CBC**
  - Hemoglobin [3, 20]: ×0.1 (g/L), ×1.611 (mmol/L)
  - Hematocrit [10, 65]: ×100 (L/L)
  - RBC_Count [1.5, 7], WBC_Count [0.5, 50], Platelet_Count [10, 1500]: none
- **Iron studies**
  - Serum_Iron [10, 300]: ×5.59 (µmol/L)
  - TIBC [50, 600]: ×5.59 (µmol/L)
  - Transferrin_Saturation [0, 100]: none
  - Ferritin [5, 5000]: ×1 (µg/L), ×0.445 (pmol/L)
  - Reticulocyte_Count [0.1, 10]: none
- **Liver function**
  - Total_Bilirubin [0.1, 30]: ×0.058 (µmol/L)
  - Direct_Bilirubin [0, 15]: ×0.058 (µmol/L)
- **Proteins/nutrition**
  - Albumin_Serum [1, 6.5]: ×0.1 (g/L)
  - Total_Protein [3, 12]: ×0.1 (g/L)
  - Prealbumin [5, 50]: ×0.1 (mg/L), ×100 (g/L)
  - CRP [0, 50] in mg/L: ×10 (from mg/dL)
- **Lipids**
  - Total_Cholesterol [50, 500]: ×38.67 (mmol/L)
  - LDL_Cholesterol [10, 300]: ×38.67
  - HDL_Cholesterol [10, 150]: ×38.67
  - Non_HDL_Cholesterol [30, 400]: ×38.67
  - Triglycerides [30, 2000]: ×88.5
- **Glucose metabolism**
  - Glucose [20, 800]: ×18.02
  - HbA1c [3, 20]: none
  - Fructosamine [150, 600]: none
- **Uric acid**
  - Uric_Acid [1, 20]: ×0.0168 (µmol/L)
- **Urinalysis**
  - Urine_Albumin [0, 5000] in mg/L: ×10 (from mg/dL)
  - Urine_Creatinine [10, 500]: ×0.0113 (µmol/L), ×11.31 (mmol/L). The skill doc's "0.113" for mmol/L is a typo; the true factor is 11.31. Try both, and keep whichever lands in range.
  - Albumin_to_Creatinine_Ratio_Urine [0, 5000]: ×8.84 (mg/mmol)
  - Protein_to_Creatinine_Ratio_Urine [0, 20000]: ×8.84
  - Urine_Protein [0, 3000]: ×0.1 (mg/L)
  - Urine_pH [4, 9]: none
  - Urine_Specific_Gravity [1.000, 1.040]: none
- **Cardiac markers**
  - BNP [0, 5000]: ×3.46 (pmol/L)
  - NT_proBNP [0, 35000]: ×8.47 (pmol/L)
  - Troponin_I [0, 50]: ×1 (µg/L), ×0.001 (ng/L)
  - Troponin_T [0, 10]: ×1 (µg/L), ×0.001 (ng/L)
- **Thyroid**
  - Free_T4 [0.2, 6]: ×0.078 (pmol/L)
  - Free_T3 [1, 10]: ×0.651 (pmol/L)
- **Blood gases**
  - pH_Arterial [6.8, 7.8]: none
  - pCO2_Arterial [15, 100]: ×7.5 (kPa)
  - pO2_Arterial [30, 500]: ×7.5 (kPa)
  - Lactate [0.3, 20] in mmol/L: ×0.111 (from mg/dL)
- **Dialysis**
  - Beta2_Microglobulin [0.5, 50]: none
  - Aluminum [0, 200]: ×26.98 (µmol/L)

**Pitfalls:**
- Match the column names exactly against the input header. Print any lab column that is not in your dict, look up its meaning in the descriptions file, and add it.
- For features whose minimum is 0, only values above the maximum get converted.
- Urine_Specific_Gravity ends up looking like `1.02` after 2-decimal rounding; that is fine.
- Parse formats before checking ranges.
- Write with `df.to_csv('/root/ckd_lab_data_harmonized.csv', index=False)`. All cells must be strings formatted `X.XX`, which avoids pandas reformatting them.

**Plan:**
1. Run the inspection commands above.
2. Write `/root/harm.py` containing a `RANGES = {col: (lo, hi, [factors])}` dict, `parse()`, `convert()`, row dropping, and formatting.
3. Run the script.
4. Validate with a single python one-liner. Re-read the output with `dtype=str` and check:
   - The column count is 62.
   - Every lab cell matches `^-?\d+\.\d{2}$`.
   - There is no `e` and no `,`.
   - Per column, count the values outside `[lo, hi]`; this should be 0. Inspect any offenders and adjust factors or tolerance.
   - Print the row counts before and after dropping.
