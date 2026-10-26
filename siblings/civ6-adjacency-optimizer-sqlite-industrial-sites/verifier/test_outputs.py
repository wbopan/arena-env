import csv
import sqlite3
from pathlib import Path

P = Path('/root/work')

def distance(a,b):
    def axial(p):
        x,y=p
        return x-(y-y%2)//2,y
    q,r=axial(a)
    s,t=axial(b)
    return max(abs(q-s),abs(r-t),abs(q+r-s-t))

def expected():
    db=sqlite3.connect(P/'industry.sqlite')
    db.row_factory=sqlite3.Row
    tiles=[dict(t) for t in db.execute('SELECT * FROM Tiles')]
    cities=[dict(c) for c in db.execute('SELECT * FROM Cities ORDER BY city_id')]
    built=[dict(b) for b in db.execute('SELECT * FROM Built')]
    positions={t['tile_id']:(t['x'],t['y']) for t in tiles}
    occupied={positions[b['tile_id']] for b in built} | {(c['x'],c['y']) for c in cities}
    aqueduct={positions[b['tile_id']] for b in built if b['district']=='AQUEDUCT'}
    result=[]
    for city in cities:
        choices=[]
        for site in tiles:
            pos=(site['x'],site['y'])
            if pos in occupied or distance(pos,(city['x'],city['y']))>2 or site['terrain']=='MOUNTAIN' or site['resource']=='IRON':
                continue
            adj=[t for t in tiles if distance(pos,(t['x'],t['y']))==1]
            score=2*sum((t['x'],t['y']) in aqueduct for t in adj)
            score+=sum(t['improvement']=='QUARRY' for t in adj)
            score+=sum(t['improvement']=='MINE' for t in adj)//2
            score+=sum(t['improvement']=='LUMBER_MILL' for t in adj)//2
            score+=sum(distance(pos,p)==1 for p in occupied)//2
            choices.append((score,site['x'],site['y']))
        score,x,y=min(choices,key=lambda v:(-v[0],v[2],v[1]))
        result.append({'city_id':city['city_id'],'x':x,'y':y,'bonus':score})
    db.close()
    return result

def rows():
    with (P/'industry_answer.csv').open(newline='') as f:
        reader=csv.DictReader(f)
        assert reader.fieldnames==['city_id','x','y','bonus']
        return [dict((k,int(v)) for k,v in row.items()) for row in reader]

def test_file():
    assert (P/'industry_answer.csv').is_file()

def test_schema_and_order():
    actual=rows()
    assert len(actual)==len(expected())
    assert [r['city_id'] for r in actual]==[r['city_id'] for r in expected()]

def test_selected_sites():
    assert [(r['x'],r['y']) for r in rows()]==[(r['x'],r['y']) for r in expected()]

def test_bonuses():
    assert [r['bonus'] for r in rows()]==[r['bonus'] for r in expected()]
