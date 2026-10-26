# Lagged associations with lake warming

Annual measurements for 2000–2032 are in four CSV files under `/root/work/`. `water_temperature.csv` has `Year,WaterTemp` in degrees C. `climate.csv` has `Year,AirTemp,WindSpeed`; `hydrology.csv` has `Year,Inflow`; and `land_cover.csv` has `Year,DevelopedPct`. Files may have different row orders. The four drivers represent Heat, Wind, Flow, and Human, respectively.

For the response and each driver, first calculate annual changes: the value in year t minus its value in year t−1. For each driver, compare the water-temperature change in every year from 2004 through 2032 inclusive with the driver's change in year t−L, separately for lags L=0, 1, and 2. Calculate the ordinary Pearson correlation for each comparison. Select the lag with the greatest absolute correlation for that driver; if there is an exact tie, select the smaller lag. This is an association measure, not a causal contribution or an R² decomposition.

Write exactly `/root/work/lagged_associations.csv`, with header `category,driver,lag_years,pearson_r,abs_r_pct` and exactly four data rows in category order Heat, Flow, Wind, Human. Use the driver names from the input headers. `pearson_r` is signed and `abs_r_pct` is 100 times its absolute value; round both to six decimal places. Lag is an integer number of years.
