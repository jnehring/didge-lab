from cad.calc.parameters import MutationParameterSet, MutationParameter, EvolveGeoParameter
import random
from cad.calc.geo import Geo, geotools
from cad.calc.didgedb import DidgeMongoDb
from cad.calc.loss import ScaleLoss
from cad.calc.mutation import evolve_finetune, ExploringMutator, evolve_explore, FinetuningMutator
from cad.calc.parameters import BasicShapeParameters, AddBubble
from cad.calc.didgmo import didgmo_high_res
from tqdm import tqdm
import logging
import pickle
import pandas as pd
from cad.calc.visualization import visualize_geo_fft, DidgeVisualizer
import math
import matplotlib.pyplot as plt
from cad.common.mt import Producer, produce_and_iterate 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - {%(filename)s:%(lineno)d} - %(levelname)s: %(message)s')
fundamental=-31
loss=ScaleLoss(scale=[0,3,5,7,10], fundamental=fundamental, n_peaks=8, octave=True)

def search_in_db(poolsize, early_stop=-1):
    db=DidgeMongoDb()

    c=0
    target_notes=[fundamental, fundamental+12, fundamental+24, fundamental-12]
    #target_notes=[fundamental]
    pool=[]
    
    #f={"parameterset": "<class '__main__.RoundedDidge'>"}
    f={}
    total=db.get_collection().count_documents(filter=f)
    pbar=tqdm(total=total)

    for o in db.get_collection().find(f):
        c+=1

        if c==early_stop:
            break

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

pkl_file="projects/temp/temp.pkl"
pool_size=10

logging.info("searching for candidates in db")
pool=search_in_db(pool_size)

logging.info("mutating candidates")
n_generations=100
n_iterations_per_generation=100

from cad.calc.mutation import Evolver
class MutationProducer(Producer):

    def __init__(self, mutator, father, loss, n_iterations, n_pool_size, pbar):
        
        self.evolver=Evolver(father, loss, mutator, n_iterations, n_poolsize=n_pool_size, pbar=pbar, show_progress=True)

    def run(self, queue):
        self.evolver.run()
        for m in self.evolver.pool:
            queue.put(m)

def pooling_mutation(mutator, pool, n_generations, n_iterations_per_generation, loss, best_loss=-1):
    pool_size=len(pool)
    n_total=n_generations*pool_size*n_iterations_per_generation
    pbar=tqdm(total=n_total)
    for i_generation in range(n_generations):
        pbar.set_description(f"generation={i_generation}, best_loss={best_loss:.2f}")
        producers=[]
        for i in range(pool_size):
            mp=MutationProducer(mutator, pool[i], loss, n_iterations_per_generation, pool_size, pbar)
            producers.append(mp)
        pool=list(produce_and_iterate(producers))
        pkl.dump(pool, open(pkl_file, "wb"))
        best_loss=pool[0]["loss"]
        pool=[p["mutant"] for p in pool]

logging.info(f"start pooling mutation with poolsize={len(pool)}, n_generations={n_generations}, n_iterations_per_generation={n_iterations_per_generation}")
best_loss=pool[0][2]
logging.info(f"initial best loss={best_loss:.2f}")
pool=[AddBubble(p[0]) for p in pool]
mutator=FinetuningMutator()
pooling_mutation(mutator, pool, n_generations, n_iterations_per_generation, loss, best_loss=best_loss)

# i=0
# for p in pool:
#     geo=p[0]
#     fft=didgmo_high_res(geo)
#     print(i)
#     i+=1
#     l=loss.get_loss(geo)
#     geotools.print_geo_summary(geo, peak=fft.peaks, loss=l)
#     print(geo.geo)

#geo=[[0.0, 32], [903.4265490017885, 44.74696440831961], [1043.2783924481641, 43.520495439677866], [1167.5572483229255, 56.05287987234595], [1265.8172834833592, 59.372000817740116], [1361.0641095223732, 75.9832280080771], [1424.7784835799014, 79.32653417809952], [1531.5316609725612, 110.29806559536875], [1634.4641691886077, 117.651508890613], [1785.0643420008407, 143.5795381422663], [1907.2298859137284, 196.87608436044138], [2113.0, 198.08650024980747]]
# geo=Geo(geo=geo)

# fft=didgmo_high_res(geo)
# l=loss.get_loss(geo, fft.peaks)
# geotools.print_geo_summary(geo, peak=fft.peaks, loss=l)


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


