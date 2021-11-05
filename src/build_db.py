from cad.calc.didgedb import search_db, build_db
from cad.calc.parameters import MutationParameterSet
import random
from cad.calc.geo import Geo, geotools

class ExploringShape(MutationParameterSet):

    def __init__(self):        
        super(ExploringShape, self).__init__()

    def make_geo(self):

        n_segments=random.randrange(8,20)
        final_length=random.randrange(2000, 3000)
        shape=[[0,32]]


        x=final_length*(0.2*random.random() + 0.3)
        y=shape[0][1]*(1+0.5*random.random())
        shape.append([x,y])

        xd=(final_length-x)/n_segments
        for i in range(n_segments-1):
            x=shape[-1][0] + xd*(random.random()+0.5)
            y=shape[-1][1] * (0.5*random.random()+0.9)
            shape.append([x,y])

        bell_y=shape[-1][1] * (1+random.random())
        bell_x=shape[-1][0] + random.randrange(80, 300)
        shape.append([bell_x, bell_y])
            
        geo=Geo(geo=shape)
        geotools.scale_length(geo, final_length)

        max_diameter=400
        if geotools.get_max_d(geo) > max_diameter:
            geotools.scale_diameter(geo, max_diameter)

        return geo

dbfolder="projects/didgedb/2"


es=ExploringShape()

build_db(dbfolder, es)
            

def search(geo, peak):
    index=0
    if peak.loc[0]["freq"] < 70:
        index+=1
    return peak.iloc[index]["note-name"] == "D1"
    #return peak.iloc[index]["note-name"]=="D1"

#geos, peaks=list(zip(*searchdb(search)))
#for p in peaks:
#    print(p[0:4])
#for geo, peak in searchdb(search):
#    print(peak)
#    break