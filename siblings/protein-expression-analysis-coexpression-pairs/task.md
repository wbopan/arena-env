# Protein co-expression pairs

The workbook `/root/work/coexpression_panel.xlsx` contains two sheets. `Data` has a `Protein_ID` column and six sample columns containing log2 expression measurements. `Pairs` has columns `Pair_ID`, `Protein_A`, and `Protein_B`; each row names two proteins to compare. The protein rows on `Data` and the rows on `Pairs` have no special ordering. Every requested protein has a numeric measurement in every sample.

Create exactly one output file, `/root/work/coexpression_pairs.json`. It must be a JSON object with exactly two keys: `pairs` and `strongest_pair_id`. `pairs` is an array containing one object for each row of the `Pairs` sheet. Each object has exactly these fields: `pair_id`, `protein_a`, `protein_b`, and `pearson_r`. Copy the first three fields from that workbook row, preserving which protein is A and which is B. Calculate `pearson_r` as the Pearson correlation coefficient between their six log2-expression measurements, matching samples by column header. Round each coefficient to four decimal places as a JSON number.

Sort the array by descending absolute value of the unrounded correlation. Break any ties by ascending `pair_id`. Set `strongest_pair_id` to the first array entry’s `pair_id`. Correlations are dimensionless; do not substitute fold changes or correlations of group averages.
