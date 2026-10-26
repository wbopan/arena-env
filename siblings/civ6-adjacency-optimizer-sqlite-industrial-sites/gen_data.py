import random
import sqlite3
from pathlib import Path

random.seed(8162)
p = Path('industry.sqlite')
if p.exists():
    p.unlink()
db = sqlite3.connect(p)
db.executescript('CREATE TABLE Cities(city_id INTEGER PRIMARY KEY,x INTEGER,y INTEGER); CREATE TABLE Tiles(tile_id INTEGER PRIMARY KEY,x INTEGER,y INTEGER,terrain TEXT,resource TEXT,improvement TEXT); CREATE TABLE Built(city_id INTEGER,district TEXT,tile_id INTEGER);')
centers = [(1,2,2),(2,7,4)]
db.executemany('INSERT INTO Cities VALUES (?,?,?)', centers)
reserved = {(2,2),(7,4),(3,2),(6,4)}
for y in range(7):
    for x in range(10):
        terrain = 'MOUNTAIN' if random.random() < .13 else 'PLAINS'
        resource = 'IRON' if random.random() < .09 else None
        improvement = random.choice([None,None,'MINE','LUMBER_MILL','QUARRY'])
        if (x,y) in reserved:
            terrain, resource, improvement = 'PLAINS', None, None
        db.execute('INSERT INTO Tiles VALUES (?,?,?,?,?,?)',(y*10+x,x,y,terrain,resource,improvement))
db.executemany('INSERT INTO Built VALUES (?,?,?)',[(1,'AQUEDUCT',23),(2,'AQUEDUCT',46)])
db.commit()
db.close()
