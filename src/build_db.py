from cad.calc.didgedb import build_db, PickleDB
from cad.calc.parameters import ExploringShape
import random
from cad.calc.didgmo import didgmo_high_res
from cad.calc.geo import Geo, geotools
import concurrent.futures
from cad.calc.mutation import Reporter, MutationParameterSet, ExploringMutator
import numpy as np
import math
import time

class RoundedDidge(MutationParameterSet):

    def __init__(self):
        super(RoundedDidge, self).__init__()

        max_n_segments=10
        self.add_param("n_segments", 1, max_n_segments, value=3)
        self.add_param("length", 1300, 3000)
        self.add_param("bellsize", 80, 300)
        self.add_param("straight_length", 1000, 2000)
        self.add_param("straight_widening", 1, 3)
        for i in range(max_n_segments):
            self.add_param(f"{i}length", 1000, 2000)
            self.add_param(f"{i}wide", 1, 3)
        self.add_param("bell", 0.2, 1)

        self.set("2wide", 3)

    def after_mutate(self):
        self.toint("length")
        self.toint("bellsize")
        self.toint("n_segments")

    def sigmoid(self, x):
        return 0.5*(1+math.tanh((x)/2))

    def make_curve(self, length, height, offset_x=0, offset_y=0, end=1.0, n_points=10):
        shape=[]

        start=0.0
        interval=(end-start)/n_points
        for a in np.arange(start, end+interval, interval):
            x=a*length + offset_x
            y=height*self.sigmoid((a*10)-5) + offset_y
            shape.append([x,y])
        return shape

    def make_geo(self):

        shape=[[0, 32]]
        x=self.get_value("straight_length")
        y=shape[-1][1] * self.get_value("straight_widening")
        shape.append([x,y])

        n_segments=self.get_value("n_segments")
        for i in range(n_segments):
            seg_length=1000
            seg_height=30
            bell=1
            if i==n_segments-1:
                bell=self.get_value("bell")
            new_shape=self.make_curve(seg_length, seg_height, offset_x=shape[-1][0], offset_y=shape[-1][1], end=bell)
            shape.extend(new_shape)

        geo=Geo(geo=shape)
        geo=geotools.scale_length(geo, self.get_value("length"))
        if geo.geo[-1][1]>self.get_value("bellsize"):
            geo=geotools.scale_diameter(geo, self.get_value("bellsize"))
        return geo

n_threads=2
n_iterations_per_thread=3
n_iterations_total=n_threads*n_iterations_per_thread

build_db(RoundedDidge(), ExploringMutator(), 3, "rounded_didge", db=PickleDB())

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