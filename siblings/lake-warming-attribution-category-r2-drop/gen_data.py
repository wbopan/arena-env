import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
years = np.arange(1985, 2025)
n = len(years)
t = years - 1985
air = 10 + 0.04 * t + rng.normal(0, 0.5, n)
sw = 150 + 2.0 * (air - 10) + rng.normal(0, 4, n)
lw = 300 + 3.0 * (air - 10) + rng.normal(0, 5, n)
hum = 70 + rng.normal(0, 3, n)
precip = 800 + rng.normal(0, 80, n)
inflow = 20 + 0.02 * (precip - 800) + rng.normal(0, 2, n)
outflow = 0.9 * inflow + rng.normal(0, 1.5, n)
wind = 4 - 0.01 * t + rng.normal(0, 0.3, n)
dev = 5 + 0.15 * t + rng.normal(0, 0.3, n)
agr = 40 - 0.1 * t + rng.normal(0, 0.5, n)
wt = (8 + 0.6 * (air - 10) + 0.015 * (sw + lw - 450) - 0.5 * (wind - 4)
      - 0.04 * (inflow - 20) + 0.05 * (dev - 5) + rng.normal(0, 0.3, n))
r = lambda a: np.round(a, 2)
pd.DataFrame({'Year': years, 'WaterTemp': r(wt)}).to_csv('water_temperature.csv', index=False)
pd.DataFrame({'Year': years, 'AirTemp': r(air), 'Shortwave': r(sw), 'Longwave': r(lw),
              'Humidity': r(hum), 'WindSpeed': r(wind)}).to_csv('climate.csv', index=False)
hyd = pd.DataFrame({'Year': years, 'Precip': r(precip), 'Inflow': r(inflow), 'Outflow': r(outflow)})
hyd = hyd[~hyd['Year'].isin([1990, 2003])]
hyd.sample(frac=1.0, random_state=1).to_csv('hydrology.csv', index=False)
lc = pd.DataFrame({'Year': years, 'DevelopedArea': r(dev), 'AgricultureArea': r(agr)})
lc = lc[lc['Year'] != 2024]
lc.to_csv('land_cover.csv', index=False)
