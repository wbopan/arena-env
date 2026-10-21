# Differential protein expression: Welch t-test with FDR control

The workbook `/root/work/protein_expression.xlsx` holds quantitative proteomics data from cancer cell lines. It has two sheets.

- **Data**: column `Protein_ID`, then one column per sample. Values are already log2-transformed intensities. Sample headers look like `MDAMB468_BREAST_TenPx01`.
- **Design**: columns `Sample` (exactly matching a Data header) and `Group`. Group is `Control`, `Treated`, or `QC`. QC samples are pooled reference runs and must be excluded from every calculation.

For every protein in the Data sheet, compute:

- `mean_control` and `mean_treated`: arithmetic means of the log2 values in each group.
- `log2fc` = mean_treated - mean_control.
- `p_value`: two-sided Welch's unequal-variance t-test comparing the treated values with the control values.
- `q_value`: the Benjamini-Hochberg adjusted p-value, computed over all proteins in the sheet. It must be monotone and capped at 1.
- `significant`: `yes` if q_value < 0.05 and |log2fc| >= 1, otherwise `no`.

Write `/root/work/results.csv` as a comma-separated file with a header row. The columns must be exactly `protein_id,mean_control,mean_treated,log2fc,p_value,q_value,significant`, in that order. Include one row per protein, in the same order as the Data sheet. Do not round the numeric values; give them at full precision, with at least 6 significant digits.
