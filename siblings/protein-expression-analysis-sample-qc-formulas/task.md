# Spreadsheet sample-quality summary

Open `/root/work/expression_panel.xlsx`. Its `Data` sheet contains log2 protein-expression measurements: column A holds protein IDs, and the remaining columns are samples. Some measurement cells are empty. The `Metadata` sheet has `Sample_ID` and `Group` columns; its sample order differs from the order of columns on `Data`.

Produce exactly one output file, `/root/work/sample_qc.xlsx`. Preserve both input sheets and their existing cells. Add a sheet named `QC` with headers `Sample_ID`, `Group`, `Detected_Proteins`, `Mean_Log2`, and `SD_Log2` in A1:E1. Add one row per `Metadata` entry, in metadata order. Columns A and B must contain the corresponding sample ID and group. For each sample, columns C through E must contain Excel formulas referring to that sample’s complete measurement column on `Data`, from its first through its last protein row.

Detected proteins means the count of numeric measurements, excluding blanks. Mean and standard deviation use only those measurements; the standard deviation is the sample statistic with denominator n−1. Do not round formula results. Set the number format of cells in columns D and E to `0.0000`, displaying four decimal places in log2 units. All samples have at least two measurements.
