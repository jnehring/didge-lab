from cad.calc.geo import Geo, geotools
from cad.calc.didgedb import DidgeMongoDb, search_db
from pymongo import MongoClient

#db["shapes"].drop()
#for x in db["shapes"].find():
#    print(x)
# print(id)
db=DidgeMongoDb()

dbfolder="projects/didgedb/2"

batch_size=5
geos=[]
peaks=[]
for geo, peak in search_db(dbfolder, lambda x,y : True):

    geos.append(geo)
    peaks.append(peak)

    if len(geos)==batch_size:
        db.save_batch(geos=geos, peaks=peaks)
        geos=[]
        peaks=[]
        break

