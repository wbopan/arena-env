#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_industry.py <<'PY'
import csv
import sqlite3

def cube(x,y):
    q=x-(y-(y&1))//2
    return q,-q-y,y

def dist(a,b):
    return sum(abs(u-v) for u,v in zip(cube(*a),cube(*b)))//2

con=sqlite3.connect('industry.sqlite')
con.row_factory=sqlite3.Row
tiles=[dict(r) for r in con.execute('SELECT * FROM Tiles')]
cities=[dict(r) for r in con.execute('SELECT * FROM Cities ORDER BY city_id')]
built=[dict(r) for r in con.execute('SELECT * FROM Built')]
by_id={t['tile_id']:(t['x'],t['y']) for t in tiles}
occupied={by_id[b['tile_id']] for b in built} | {(c['x'],c['y']) for c in cities}
aq={by_id[b['tile_id']] for b in built if b['district']=='AQUEDUCT'}
rows=[]
for c in cities:
    scores=[]
    for t in tiles:
        p=(t['x'],t['y'])
        if p in occupied or dist(p,(c['x'],c['y']))>2 or t['terrain']=='MOUNTAIN' or t['resource']=='IRON':
            continue
        neighbors=[n for n in tiles if dist(p,(n['x'],n['y']))==1]
        value=2*sum((n['x'],n['y']) in aq for n in neighbors)
        value+=sum(n['improvement']=='QUARRY' for n in neighbors)
        value+=sum(n['improvement']=='MINE' for n in neighbors)//2
        value+=sum(n['improvement']=='LUMBER_MILL' for n in neighbors)//2
        value+=sum(dist(p,q)==1 for q in occupied)//2
        scores.append((value,p))
    bonus,(x,y)=min(scores,key=lambda z:(-z[0],z[1][1],z[1][0]))
    rows.append((c['city_id'],x,y,bonus))
con.close()
with open('industry_answer.csv','w',newline='') as f:
    writer=csv.writer(f)
    writer.writerow(['city_id','x','y','bonus'])
    writer.writerows(rows)
PY
python /tmp/solve_industry.py
