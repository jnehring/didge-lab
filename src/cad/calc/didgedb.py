from cad.calc.didgmo import didgmo_high_res
from cad.calc.geo import Geo
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

    def save_batch(self, geos=None, peaks=None, ffts=None):
        batch=[]
        for i in range(len(geos)):
            peak=peaks[i]

            if len(peaks[i])==0:
                continue

            peak=peak.to_dict("records")
            geo=geotools.geo_to_json(geos[i])
            s={
                "geo": geo,
                "peak": peak
            }
            batch.append(s)
        self.get_collection().insert_many(batch)

    def unserialize(self, s):
        geo=Geo(geo=s["geo"])
        peak=pd.DataFrame(s["peak"])
        return geo, peak


def build_db(folder, father, n_batches=100, n_didges_per_patch=500):
    m=ExploringMutator()

    pbar=tqdm(total=n_didges_per_patch*n_batches)
    for i in range(0, n_batches):

        ffts=[]
        geos=[]
        peaks=[]
        for j in range(0, n_didges_per_patch):
            pbar.update(1)
            try:
                p=father.copy()
                m.mutate(p)
                p.after_mutate()

                geo=p.make_geo()
                fft=didgmo_high_res(geo)

                ffts.append(fft)
                geos.append(geo)
                peaks.append(fft.peaks)
            except Exception as e:
                pass
                
        #pickle.dump(ffts, open(os.path.join(folder, f"fft_{i}.pkl"), "wb"))
        pickle.dump(geos, open(os.path.join(folder, f"geo_{i}.pkl"), "wb"))
        pickle.dump(peaks, open(os.path.join(folder, f"peak_{i}.pkl"), "wb"))

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
