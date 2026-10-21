# Demand-side GDP impact of an investment shock

Inputs in /root/work:
- `weo.xlsx`, sheet `WEO_Data`. Row 1 holds headers, then there is one row per year with the columns Year, Nominal GDP (bn GEL), Real GDP growth (%) and GDP deflator (2019=100). Historical years have all four columns filled. Projection years have only real growth; their other cells are blank.
- `params.json` with these keys:
  - total_investment_usd_bn
  - fx_gel_per_usd
  - demand_multiplier
  - import_content_share
  - start_year
  - allocation_weights: one weight per project year, in order, not normalised.

Method (let L be the last year that has both nominal GDP and the deflator D):
1. Deflator growth g = the arithmetic mean of the four annual rates D_t/D_(t-1) - 1 for t = L-3 .. L. Extend D_t = D_(t-1) * (1+g) for t > L.
2. Real GDP R (bn GEL, 2019 prices): R_L = Nominal_L / D_L * 100, and R_t = R_(t-1) * (1 + growth_t/100) for t > L.
3. For each project year t = start_year + k (k = 0..n-1, with weight w_k):
   - Investment_GEL = total * fx * w_k / sum(w) (bn GEL, nominal);
   - Real_Investment = Investment_GEL / D_t * 100;
   - GDP_Impact = Real_Investment * (1 - import_content_share) * demand_multiplier;
   - Impact_pct = GDP_Impact / R_t * 100.

Output `/root/work/shock_impact.xlsx`, sheet `Impact`:
- Row 1 holds exactly these headers: `Year, Deflator, Real_GDP, Investment_GEL, Real_Investment, GDP_Impact, Impact_pct`.
- Rows 2 onward hold one row per project year, in ascending order.
- Every cell must contain a numeric value, not a formula.
- Year is an integer. Leave the other columns unrounded or round them to at least 6 decimals.
