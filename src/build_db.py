from cad.calc.didgedb import build_db, PickleDB, DidgeMongoDb
from cad.calc.parameters import ExploringShape, RoundedDidge
import random
from cad.calc.didgmo import didgmo_high_res
from cad.calc.geo import Geo, geotools
import concurrent.futures
from cad.calc.mutation import Reporter, MutationParameterSet, ExploringMutator
import numpy as np
import math
import time


n_threads=2
n_iterations_per_thread=3
n_iterations_total=n_threads*n_iterations_per_thread

build_db(RoundedDidge(), ExploringMutator(), 1000000, "rounded_didge",  n_threads=20, db=DidgeMongoDb(), batch_size=100)

# rd=RoundedDidge()
# mutator=ExploringMutator()
# mutator.mutate(rd)
# rd.after_mutate()
# rd.make_geo()
#build_db(RoundedDidge())

    #return peak.iloc[index]["note-name"]=="D1"

#geos, peaks=list(zip(*searchdb(search)))
#for p in peaks:
#    print(p[0:4])
#for geo, peak in searchdb(search):
#    print(peak)
#    break