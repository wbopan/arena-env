# Median-normalized fold changes for target proteins

The workbook `/root/work/raw_intensity.xlsx` contains raw (linear, not log-transformed) protein intensities. It has three sheets.

- **Data**: column `Protein_ID`, then one column per sample. Each sample header has the form `<CELLLINE>_<TISSUE>_<Sample_ID>`, for example `HCT116_LARGE_INTESTINE_TenPx03`. The Sample_ID is the part after the last underscore. An empty cell or a value of 0 means the value is missing.
- **Samples**: columns `Sample_ID` (short IDs such as `TenPx03`) and `Condition` (`Control` or `Treated`).
- **Targets**: column `Protein_ID`, listing the proteins to report.

## Processing

1. Take log2 of every non-missing intensity.
2. Median-normalize each sample. Subtract that sample's median log2 value, taken over all proteins in the Data sheet that have a value in that sample.
3. For each target protein, ignore missing values and compute:
   - the number of non-missing values per condition;
   - the mean normalized value per condition;
   - `Log2FC` = Mean_Treated - Mean_Control;
   - `Fold_Change` = 2^Log2FC.

## Output

Create `/root/work/target_summary.xlsx` with a sheet named `Summary`. Row 1 must hold exactly these headers: `Protein_ID, N_Control, N_Treated, Mean_Control, Mean_Treated, Log2FC, Fold_Change`. Write one row per target protein, in the order of the Targets sheet.

Cells must contain numeric values, not formulas. Write counts as integers. Round the other numbers to 4 decimals, computing Fold_Change from the unrounded Log2FC.
