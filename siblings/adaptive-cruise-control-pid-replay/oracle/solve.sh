#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_replay.py << 'EOF'
import pandas as pd
import yaml

cfg = yaml.safe_load(open('acc_config.yaml'))
a, lim, g, dt = cfg['acc'], cfg['limits'], cfg['gains'], float(cfg['dt'])

class PID:
    def __init__(self, kp, ki, kd):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.reset()
    def reset(self):
        self.i = 0.0
        self.prev = None
    def step(self, e):
        self.i += e * dt
        der = 0.0 if self.prev is None else (e - self.prev) / dt
        self.prev = e
        return self.kp * e + self.ki * self.i + self.kd * der

sp = PID(**g['pid_speed'])
dp = PID(**g['pid_distance'])
df = pd.read_csv('sensor_log.csv')
prev = None
with open('commands.csv', 'w') as f:
    print('time,mode,accel_cmd,distance_error,ttc', file=f)
    for r in df.itertuples(index=False):
        de = None
        ttc = None
        if pd.isna(r.lead_speed) or pd.isna(r.distance):
            mode = 'cruise'
        else:
            de = r.distance - (a['min_distance'] + a['time_headway'] * r.ego_speed)
            rel = r.ego_speed - r.lead_speed
            if rel > 0:
                ttc = r.distance / rel
            mode = 'emergency' if (ttc is not None and ttc < a['ttc_threshold']) else 'follow'
        if mode != prev:
            sp.reset(); dp.reset()
        if mode == 'cruise':
            u = sp.step(a['set_speed'] - r.ego_speed)
        elif mode == 'follow':
            u = dp.step(de)
        else:
            u = lim['max_decel']
        u = min(max(u, lim['max_decel']), lim['max_accel'])
        prev = mode
        des = '' if de is None else f'{de:.3f}'
        ts = '' if ttc is None else f'{ttc:.3f}'
        print(f'{r.time:.1f},{mode},{u:.4f},{des},{ts}', file=f)
EOF
python3 /tmp/solve_replay.py
