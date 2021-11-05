from cad.calc.parameters import MutationParameterSet
import random
from cad.calc.geo import Geo, geotools
from cad.calc.didgedb import DidgeMongoDb
from cad.calc.loss import ScaleLoss
from tqdm import tqdm

db=DidgeMongoDb()

c=0
target_notes=[-31, -19, 7]

loss=ScaleLoss(scale=[0,3], fundamental=-31, n_peaks=2)

pool=[]
poolsize=10

total=db.get_collection().count()
pbar=tqdm(total=total)

for o in db.get_collection().find():

    c+=1
    count=0
    pbar.update(1)
    for p in o["peak"][0:3]:

        if p["note-number"] in target_notes:
            count+=1
    if count<2:
        continue

    geo, peak = db.unserialize(o)
    geoloss=loss.get_loss(geo, peaks=peak)
    pool.append((geo, peak, geoloss))

    sorted(pool, key=lambda x : x[2])
    if len(pool)>poolsize:
        pool=pool[0:poolsize]

geo, peak, _ = pool[0]    
geotools.print_geo_summary(geo, peak)

# def search(geo, peak):
#     index=0
#     if peak.loc[0]["freq"] < 70:
#         index+=1

#     decision=peak.iloc[index]["note-name"] == "D1" and peak.iloc[index+1]["note-name"] == "D2"
#     return decision
#     #return peak.iloc[index]["note-name"]=="D1"

# for geo, peak in search_db("projects/didgedb/2/", search):
#     geotools.print_geo_summary(geo, peak)
#     print()
