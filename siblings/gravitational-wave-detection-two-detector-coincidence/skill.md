## Reference notes

These files contain **trigger peaks**, not strain samples. No filtering, PSD estimation, waveform generation, or matched filtering is needed; the supplied `snr` values are already nonnegative magnitudes.

- Use Python’s standard-library `csv.DictReader` to read each catalog. Keep `trigger_id` as a string. `decimal.Decimal` can parse the numeric CSV fields and preserve the stated inclusive cutoffs and exact tie comparisons without floating-point boundary surprises.
- Examine **pairs across the two catalogs**; neither member needs to be its detector’s loudest trigger. Accept a pair when both `abs(L_time - H_time) <= Decimal("0.012")` and `abs(L_mass - H_mass) <= Decimal("2.0")`.
- Network SNR is `sqrt(H_snr**2 + L_snr**2)`. Compare the **unrounded sum of squares** to rank pairs (square root is monotonic for nonnegative values). On an exact tie, compare `(H_id, L_id)` lexicographically as strings.
- For the selected pair, `delay_ms = (L_time - H_time) * 1000` and `mean_total_mass_solar = (H_mass + L_mass) / 2`. Round the three output numbers only after selection.
- The output is one YAML mapping with exactly the requested keys. JSON-style quoted strings and numeric scalars are valid YAML; `json.dumps(id_string)` is useful for safely quoting IDs when writing mapping lines. Check the written file’s keys, scalar types, and three-decimal formatting.
