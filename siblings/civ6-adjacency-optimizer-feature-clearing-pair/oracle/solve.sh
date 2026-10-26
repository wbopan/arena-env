#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_pair.py <<'PY'
import json
from itertools import product

def cube(p):
    x,y=p
    q=x-(y-(y&1))//2
    return q,-q-y,y

def near(a,b):
    return sum(abs(i-j) for i,j in zip(cube(a),cube(b))) == 2

d=json.load(open('pair_map.json'))
spots=d['spots']
def bonuses(c,h):
    used={tuple(c),tuple(h),tuple(d['city_center'])}
    result=[]
    for p,kind in [(c,'CAMPUS'),(h,'HOLY_SITE')]:
        adj=[t for t in d['tiles'] if near(p,(t['x'],t['y']))]
        result.append(sum(t['terrain']=='MOUNTAIN' for t in adj)
            + sum(t['feature']==('JUNGLE' if kind=='CAMPUS' else 'FOREST') and (t['x'],t['y']) not in used for t in adj)//2
            + sum(near(p,v) for v in used)//2
            + (2*sum(t['feature']=='GEOTHERMAL' for t in adj) if kind=='CAMPUS' else 0))
    return result
options=[]
for c,h in product(spots['CAMPUS'],spots['HOLY_SITE']):
    if c!=h:
        b=bonuses(c,h)
        options.append((sum(b),c,h,b))
t,c,h,b=min(options,key=lambda v:(-v[0],v[1][1],v[1][0],v[2][1],v[2][0]))
with open('pair_answer.json','w') as f:
    json.dump({'placements':{'CAMPUS':c,'HOLY_SITE':h},'bonuses':{'CAMPUS':b[0],'HOLY_SITE':b[1]},'total':t},f)
PY
python /tmp/solve_pair.py
