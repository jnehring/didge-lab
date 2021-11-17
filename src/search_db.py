from cad.calc.didgedb import DidgeMongoDb

db=DidgeMongoDb()

print(db.get_collection().count())
#for result in db.get_collection().find():
#    print(result)