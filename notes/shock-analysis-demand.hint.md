1. Inspect the template's labels and formulas (WEO_Data, SUT Calc, NA D30–D33) and any local WEO/Geostat files with small openpyxl one-liners.
2. In one openpyxl script, copy the SUPPLY/USE sheets (names unchanged) and enter raw WEO data. Write everything else as formulas: 2027 growth held to 2043, deflator extended at the 4-year average growth, and C46 = SUM(GFCF×imports/supply)/SUM(GFCF).
3. NA: FX 2.746, multiplier 0.8, import share linked to C46, bell weights summing to 1 over 2026–2033. Then USD→GEL→real (GDP deflator) → ×(1−import share) → ×multiplier → % of GDP.
4. Copy the block twice below (multiplier 1; import share 0.5) and save as `test_demand.xlsx`.
5. Run `python recalc.py test_demand.xlsx`, require 0 errors, and spot-check values with `data_only=True` without saving.
