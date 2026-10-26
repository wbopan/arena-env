# Compare measured glucose with HbA1c-derived glucose

`/root/work/glycemic_pairs.csv` contains paired measurements with columns `patient_id,hba1c_value,hba1c_unit,glucose_value,glucose_unit`. An HbA1c result is labeled either `NGSP_percent` or `IFCC_mmol_mol`. A glucose result is labeled either `mg/dL` or `mmol/L`. Numeric cells may include surrounding spaces, comma decimal separators, or scientific notation. Every row is complete.

Create `/root/work/glycemic_comparison.csv` with exactly these columns in order: `patient_id,hba1c_percent,eag_mg_dL,glucose_mg_dL,gap_mg_dL`. Include every patient in input order. Output numeric cells as plain decimals with exactly two places, including a minus sign for negative gaps.

Convert IFCC HbA1c to NGSP percent using `IFCC / 10.929 + 2.15`; an existing NGSP percent needs no conversion. Compute estimated average glucose (eAG) in mg/dL as `28.7 × NGSP percent − 46.7`. Convert measured glucose from mmol/L to mg/dL with factor 18.02 when necessary. The gap is converted measured glucose minus eAG, in mg/dL; it may be negative. Carry unrounded values through all calculations and round only the four output measurements. Do not infer a diagnosis or discard discordant pairs.
