from cad.calc.didgedb import DidgeMongoDb, PickleDB

db=PickleDB()
for didge in db.iterate():
    print(didge)
    break

#db=DidgeMongoDb()
#print(db.get_collection().count())
#for result in db.get_collection().find():
#    print(result)