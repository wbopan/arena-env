# Driver-category contribution to lake water temperature

Annual data for one lake are in four files under `/root/work/`, all keyed by `Year`:

- `water_temperature.csv`: `Year`, `WaterTemp` (surface 0-5 m, degrees C)
- `climate.csv`: `Year`, `AirTemp`, `Shortwave`, `Longwave`, `Humidity`, `WindSpeed`
- `hydrology.csv`: `Year`, `Precip`, `Inflow`, `Outflow`
- `land_cover.csv`: `Year`, `DevelopedArea`, `AgricultureArea`

Use only the years present in all four files.

First, create the derived variable `NetRadiation = Shortwave + Longwave`. Do not use the two radiation components separately after this.

Assign the predictors to categories as follows:

- **Heat**: `AirTemp`, `NetRadiation`, `Humidity`
- **Flow**: `Precip`, `Inflow`, `Outflow`
- **Wind**: `WindSpeed`
- **Human**: `DevelopedArea`, `AgricultureArea`

Fit an ordinary least-squares regression with an intercept of `WaterTemp` on all 8 predictors. Its coefficient of determination is R2_full.

For each category, refit the regression with that category's predictors removed. The category's contribution is:

contribution = (R2_full - R2_without_category) x 100

This is in percentage points.

Write `/root/work/contributions.csv` with:

- the header `category,contribution`
- exactly four rows, one per category, using the names `Heat`, `Flow`, `Wind`, `Human`
- rows sorted by contribution, descending
- contribution values rounded to 2 decimals
