from cad.calc.didgedb import DidgeMongoDb
from cad.calc.parameters import MultiBubble

db=DidgeMongoDb()

geos=[]
peaks=[]
for i in range(100000):

    mb=MultiBubble(geo, n_bubbles)

    geos.append(geo)
    peaks.append(peak)

    if len(geos)==batch_size:
        db.save_batch(geos=geos, peaks=peaks, parameterset="ExploringShape")
        geos=[]
        peaks=[]


p=db.get_db()["didge"]["shapes"].count()
print(p)