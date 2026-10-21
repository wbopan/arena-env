#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_fit.py <<'EOF'
import json
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

df = pd.read_csv('calibration.csv')
on = df['heater_power'] > 0
t0 = float(df.loc[on, 'time'].iloc[0])
u = float(df.loc[on, 'heater_power'].iloc[0])
ya = float(df.loc[df['time'] < t0, 'temperature'].mean())
sub = df[df['time'] >= t0]
t = sub['time'].to_numpy() - t0
y = sub['temperature'].to_numpy()

def model(tt, K, tau):
    return ya + K * u * (1 - np.exp(-tt / tau))

Kg = (y[-20:].mean() - ya) / u
target = ya + 0.632 * (y[-20:].mean() - ya)
taug = max(float(t[np.argmin(np.abs(y - target))]), 1.0)
popt, _ = curve_fit(model, t, y, p0=[Kg, taug], maxfev=20000)
K, tau = float(popt[0]), float(popt[1])
res = y - model(t, K, tau)
r2 = 1 - np.sum(res ** 2) / np.sum((y - y.mean()) ** 2)
rmse = float(np.sqrt(np.mean(res ** 2)))
lam = 0.75 * tau
Kp = tau / (K * lam)
Ki = Kp / tau
out = {'K': K, 'tau': tau, 'y_ambient': ya, 'r_squared': float(r2), 'rmse': rmse, 'lambda': lam, 'Kp': Kp, 'Ki': Ki}
out = {k: round(float(v), 4) for k, v in out.items()}
with open('estimated_params.json', 'w') as f:
    json.dump(out, f, indent=2)
EOF
python3 /tmp/solve_fit.py
