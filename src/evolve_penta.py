from cad.calc.parameters import MutationParameterSet, MutationParameter, EvolveGeoParameter
import random
from cad.calc.geo import Geo, geotools
from cad.calc.didgedb import DidgeMongoDb
from cad.calc.loss import ScaleLoss
from cad.calc.mutation import evolve_finetune, ExploringMutator, evolve_explore
from cad.calc.parameters import BasicShapeParameters
from cad.calc.didgmo import didgmo_high_res
from tqdm import tqdm
import logging
import pickle
import pandas as pd
from cad.calc.visualization import visualize_geo_fft, DidgeVisualizer
import math
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - {%(filename)s:%(lineno)d} - %(levelname)s: %(message)s')
fundamental=-31
loss=ScaleLoss(scale=[0,3,5,7,10], fundamental=fundamental, n_peaks=8, octave=True)

pkl_file="projects/temp/temp.pkl"

def search_in_db():
    logging.info("searching for shape in db")
    db=DidgeMongoDb()

    c=0
    target_notes=[fundamental, fundamental+12, fundamental+24, fundamental-12]
    #target_notes=[fundamental]
    pool=[]
    poolsize=5

    #f={"parameterset": "<class '__main__.RoundedDidge'>"}
    f={}
    total=db.get_collection().count_documents(filter=f)
    pbar=tqdm(total=total)

    for o in db.get_collection().find(f):
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

        pool=sorted(pool, key=lambda x : x[2])
        if len(pool)>poolsize:
            pool=pool[0:poolsize]

    return pool

# search best geo in database 
  
pool=search_in_db()
i=0
for p in pool:
    geo=p[0]
    fft=didgmo_high_res(geo)
    print(i)
    i+=1
    l=loss.get_loss(geo)
    geotools.print_geo_summary(geo, peak=fft.peaks, loss=l)
    print(geo.geo)

#geo=[[0.0, 32], [903.4265490017885, 44.74696440831961], [1043.2783924481641, 43.520495439677866], [1167.5572483229255, 56.05287987234595], [1265.8172834833592, 59.372000817740116], [1361.0641095223732, 75.9832280080771], [1424.7784835799014, 79.32653417809952], [1531.5316609725612, 110.29806559536875], [1634.4641691886077, 117.651508890613], [1785.0643420008407, 143.5795381422663], [1907.2298859137284, 196.87608436044138], [2113.0, 198.08650024980747]]
# geo=Geo(geo=geo)

# fft=didgmo_high_res(geo)
# l=loss.get_loss(geo, fft.peaks)
# geotools.print_geo_summary(geo, peak=fft.peaks, loss=l)

class AddBubble(MutationParameterSet):

    def __init__(self, geo, n_bubbles=1):
        super(AddBubble, self).__init__()
        
        self.geo=geo
        self.n_bubbles=n_bubbles

        for i in range(0, n_bubbles):
            self.mutable_parameters.append(MutationParameter(f"{i}pos", 0.5, 0, 1))
            self.mutable_parameters.append(MutationParameter(f"{i}width", 400, 50, 450))
            self.mutable_parameters.append(MutationParameter(f"{i}height", 1, 0, 1.5))
    
    def get_index(self, shape, x):
        for i in range(len(shape)):
            if shape[i][0]>x:
                return i
        return None

    def get_y(self, shape, x):
        i=self.get_index(shape, x)
        xa=shape[i-1][0]
        xe=shape[i][0]
        ya=shape[i-1][1]
        ye=shape[i][1]
        alpha=math.atan(0.5*(ye-ya) / (xe-xa))

        xd=x-xa
        y=ya + 2*xd*math.tan(alpha)
        return y

    def make_bubble(self, shape, pos, width, height):

        shape=self.geo.geo
        n_segments=11
        pos=pos*(self.geo.length()-2*width) + width
        
        i=self.get_index(shape, pos)

        xa=shape[i-1][0]
        xe=shape[i][0]
        ya=self.get_y(shape, pos-0.5*width)
        ye=self.get_y(shape, pos+0.5*width)
        alpha=math.atan(0.5*(ye-ya) / (xe-xa))

        bubbleshape=[]

        for i in range(1, n_segments+1):
            x=pos-0.5*width + i*width/n_segments
            y=ya + 2*(x-xa)*math.tan(alpha)

            #print(math.tan(alpha), 2*(x-xa))
            factor=1+math.sin((i-1)*math.pi/(n_segments-1))*height
            y*=factor
            bubbleshape.append([x,y])

        newshape=[]

        ia=self.get_index(shape, xa)
        ie=self.get_index(shape, xe)

        newshape.extend(shape[0:ia])
        newshape.extend(bubbleshape)
        newshape.extend(shape[ie:])
        return newshape
        # geo=Geo(geo=newshape)
        # geo.sort_segments()
        # return geo.shape
        
    def make_geo(self):

        shape=self.geo.copy().geo
        for i in range(self.n_bubbles):
            pos=self.get_value(f"{i}pos")
            width=self.get_value(f"{i}width")
            height=self.get_value(f"{i}height")
            shape=self.make_bubble(shape, pos, width, height)
        return Geo(geo=shape)

# parameters=AddBubble(geo, n_bubbles=3)
# pool=evolve_explore(loss, parameters, 10, 1000)
# pickle.dump(pool, open(pkl_file, "wb"))

# geo=pool[0]["mutant"].make_geo()
# fft=didgmo_high_res(geo)
# l=loss.get_loss(geo, fft.peaks)
# geotools.print_geo_summary(geo, peak=fft.peaks, loss=l)

# pool=pickle.load(open(pkl_file, "rb"))
# for mutant in pool:

#     geo=mutant["mutant"].make_geo()
#     print(geo.geo)
#     fft=didgmo_high_res(geo)
#     l=loss.get_loss(geo, fft.peaks)
#     geotools.print_geo_summary(geo, peak=fft.peaks, loss=l)

# em.mutate(parameters)
# #print(parameters)
# geo2=parameters.make_geo()

# for x in geo2.geo:
#     print(x)
# fft=didgmo_high_res(geo2)
# l=loss.get_loss(geo2, fft.peaks)

# geotools.print_geo_summary(geo2, peak=fft.peaks, loss=l)

# #print(geo2.geo)
# #for s in geo2.geo:
# #    print(s)
# DidgeVisualizer.vis_didge(geo2)
# plt.show()

# parameters=AddBubble(geo)
# pool=evolve_explore(loss, parameters, 10, 1000)
# pickle.dump(pool, open(pkl_file, "wb"))

# pool=pickle.load(open(pkl_file, "rb"))
# geo=pool[0]["mutant"].make_geo()
# fft=didgmo_high_res(geo)
# l=loss.get_loss(geo, fft.peaks)
# geotools.print_geo_summary(geo, peak=fft.peaks, loss=l)

# finetune this geo

# parameters=[EvolveGeoParameter(x[0]) for x in pool]
# pool=evolve_finetune(loss, parameters, 1000)
# pickle.dump(pool, open(pkl_file, "wb"))

# experiment with fine tuning

# pool=pickle.load(open(pkl_file, "rb"))
# geo=pool[0]["mutant"].make_geo()
# fft=didgmo_high_res(geo)
# l=loss.get_loss(geo, fft.peaks)
# print(f"original loss: {l}")


#geotools.print_geo_summary(geo, fft.peaks, loss=l)

# table={}
# table[0]=fft.peaks["note-name"] + " " + fft.peaks["cent-diff"].apply(lambda x : str(round(x)))
# #visualize_geo_fft(geo)
# l=geo.length()
# n=5



# for i in range(1,n):
#     gc=geo.copy()
#     scale=1-i/20
#     gc.geo=[[x[0], x[1]*scale] for x in gc.geo]
#     fft=didgmo_high_res(gc)
#     table[i]=fft.peaks["note-name"] + " " + fft.peaks["cent-diff"].apply(lambda x : str(round(x)))

# df=pd.DataFrame(table)
# print(df)


