from cad.calc.geo import Geo, geotools
from cad.calc.didgedb import DidgeMongoDb, search_pkl_db
from pymongo import MongoClient

#db["shapes"].drop()
#for x in db["shapes"].find():
#    print(x)
# print(id)
db=DidgeMongoDb()
db.drop()

dbfolder="projects/didgedb/2"

batch_size=100
geos=[]
peaks=[]
c=0

for geo, peak in search_pkl_db(dbfolder, lambda x,y : True):

    geos.append(geo)
    peaks.append(peak)

    if len(geos)==batch_size:
        db.save_batch(geos=geos, peaks=peaks)
        geos=[]
        peaks=[]

if len(geos)>0:
    db.save_batch(geos=geos, peaks=peaks)

count=db.get_collection().count()
print(f"wrote {count} shapes to the database")
# for o in db.get_collection().find():
#     print(o)
#     break

