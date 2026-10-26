# Standardize arterial blood gases and estimate bicarbonate

`/root/work/arterial_gases.csv` contains arterial samples with columns `sample_id,ph,pco2_value,pco2_unit,po2_value,po2_unit`. Each gas pressure is labeled either `kPa` or `mmHg`; the labels apply independently to pCO2 and pO2. All samples are complete. Numeric cells may use a period or comma as their decimal separator and may have surrounding spaces. The pH is dimensionless and must not be converted.

Write exactly one output file, `/root/work/gas_results.json`. It must be a JSON array in input-row order, with one object per sample. Each object must have exactly the string fields `sample_id`, `pco2_mmHg`, `po2_mmHg`, and `bicarbonate_mEq_L`. Format each numeric string as a plain nonnegative decimal with exactly two places; do not include units inside the strings.

Convert pressures using the convention 1 kPa = 7.5 mmHg. After converting pCO2, estimate bicarbonate in mEq/L by the Henderson–Hasselbalch rearrangement: `0.03 × pCO2(mmHg) × 10^(pH − 6.1)`. Use the unrounded converted pressure for this calculation, then round each reported numeric field separately to two decimal places. These are calculated estimates, not independently measured bicarbonate values.
