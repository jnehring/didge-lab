from cad.calc.didgmo import didgmo_high_res
from cad.calc.geo import Geo, geotools
import math
import random
import copy
from tqdm import tqdm
from cad.calc.loss import ScaleLoss, AmpLoss, CombinedLoss
from cad.calc.mutation import *
from cad.calc.conv import freq_to_note_and_cent
from cad.calc.geo import Geo, geotools
from cad.calc.parameters import BasicShapeParameters, MutationParameterSet, MutationParameter
import pickle
from tqdm import tqdm
import os
from pymongo import MongoClient
import re
import pandas as pd
from datetime import datetime
import traceback
from cad.calc.mutation import Reporter
from multiprocessing import Pool

class DidgeMongoDb():

    def __init__(self):
        self.client=None
        self.collection="shapes"

    def get_db(self):
        if self.client==None:
            self.client = MongoClient("mongodb://localhost:27017/")
        return self.client

    def drop(self):
        self.get_collection().drop()

    def get_collection(self):
        return self.get_db()["didge"][self.collection]

    def save_batch(self, geos=None, peaks=None, ffts=None, parameterset=""):
        batch=[]
        for i in range(len(geos)):
            peak=peaks[i]

            if len(peaks[i])==0:
                continue

            peak=peak.to_dict("records")
            geo=geotools.geo_to_json(geos[i])
            s={
                "geo": geo,
                "peak": peak,
                "parameterset": parameterset,
                "creation_date": datetime.now().isoformat()
            }
            batch.append(s)
        self.get_collection().insert_many(batch)

    def unserialize(self, s):
        geo=Geo(geo=s["geo"])
        peak=pd.DataFrame(s["peak"])
        return geo, peak


import queue
import threading
from tqdm import tqdm

def build_db(father, n_iterations=10000, collection="shapes", parameterset=None):
    m=ExploringMutator()

    #reporter=Reporter(n_iterations)
    n_threads=10
    db=DidgeMongoDb()
    batch_size=100
    n_iterations_per_thread=int(n_iterations/n_threads)
    n_jobs=round(n_iterations/batch_size)
    if parameterset==None:
        parameterset=str(type(father))

    dataQueue = queue.Queue()

    processes = []

    class ProducerThread(threading.Thread):
        def __init__(self, father, n_iterations, mutator, dataQueue):
            threading.Thread.__init__(self)
            self.father=father
            self.n_iterations=n_iterations
            self.mutator=mutator
            self.dataQueue=dataQueue

        def run(self):
            for j in range(n_iterations):

                try:
                    p=self.father.copy()
                    self.mutator.mutate(p)
                    p.after_mutate()

                    geo=p.make_geo()
                    fft=didgmo_high_res(geo)
                    self.dataQueue.put((geo, fft.peaks))

                except Exception as e:
                    continue
                    #print(traceback.format_exc())
            
    class ConsumerThread(threading.Thread):

        def __init__(self, dataQueue, n_iterations):
            threading.Thread.__init__(self)
            self.dataQueue=dataQueue
            self.stop=False
            self.n_iterations=n_iterations

        def run(self):
            geos=[]
            peaks=[]
            pbar=tqdm(total=self.n_iterations)

            while not self.stop:
                d=self.dataQueue.get()
                pbar.update()
                geos.append(d[0])
                peaks.append(d[1])

                if len(geos)>=batch_size:
                    db.save_batch(geos, peaks, parameterset=parameterset)
                    geos=[]
                    peaks=[]

    threads=[]
    for i in range(n_threads):
        pt=ProducerThread(father, n_iterations_per_thread, ExploringMutator(), dataQueue)
        threads.append(pt)
        pt.start()

    ct=ConsumerThread(dataQueue, n_iterations)
    ct.start()
    for i in range(n_threads):
        threads[i].join()

    ct.stop=True

def search_pkl_db(dbfolder, searchfct):
    files=os.listdir(dbfolder)

    files=[int(maxi[maxi.find("_")+1:maxi.find(".")]) for maxi in files]
    files=sorted(files)
    maxi=files[-1]
    maxi=int(maxi)

    for i in range(maxi+1):
        peaks=pickle.load(open(os.path.join(dbfolder, f"peak_{i}.pkl"), "rb"))
        geos=pickle.load(open(os.path.join(dbfolder, f"geo_{i}.pkl"), "rb"))

        for j in range(len(peaks)):
            if len(peaks[j])==0:
                continue
            if searchfct(geos[j], peaks[j]):
                yield geos[j], peaks[j]
