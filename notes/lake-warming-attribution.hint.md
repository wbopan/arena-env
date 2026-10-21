1. Inspect: `head -3` and `wc -l` on each `/root/data/*.csv`, then check that `pymannkendall` and `factor_analyzer` import.
2. Trend: run `pymannkendall.original_test` on the annual water temperature and write `slope,p-value` to `/root/output/trend_result.csv`.
3. Drivers: merge on Year, combine Shortwave + Longwave into NetRadiation, standardize, and run one global `FactorAnalyzer(n_factors=4, rotation='varimax')`.
4. Map each factor to Heat/Flow/Wind/Human by its top loadings. Compute contribution = (R²_full − R²_without_factor) × 100.
5. Write the top category and its rounded % to `/root/output/dominant_factor.csv` with header `variable,contribution`, then `cat` both files to verify.
