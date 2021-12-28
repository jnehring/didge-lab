from cad.calc.mutation import ExploringMutator
from cad.calc.parameters import MutationParameterSet, AddBubble
# from cad.cadsd.cadsd import CADSDResult
# import pickle
# from cad.ui.ui import UserInterface, PeakWindow, StaticTextWindow
# from cad.ui.fft_window import FFTWindow
# from cad.ui.explorer import Explorer
from cad.calc.geo import Geo, geotools
import math
import random
from cad.ui.visualization import visualize_geo_to_files
import matplotlib.pyplot as plt
import os
import shutil

random.seed(0)

class ConeMutationParameter(MutationParameterSet):

    def __init__(self):
        MutationParameterSet.__init__(self)
        self.add_param("length", 1200, 2800)
        self.add_param("bell_width", 40, 120)
        self.add_param("min_t", -10, 0)
        self.add_param("max_t",0.01, 10)

        self.d1=32
        
    def make_geo(self):
        n_segments=20

        geo=[]
        min_t=self.get_value("min_t")
        max_t=self.get_value("max_t")
        t_diff=max_t-min_t
        max_y=(math.pow(2, (t_diff*n_segments/(n_segments+1))+min_t))-math.pow(2, min_t)
        for i in range(n_segments+1):
            x=self.get_value("length")*i/n_segments
            y=((math.pow(2, (t_diff*i/(n_segments+1))+min_t))-math.pow(2, min_t))/max_y
            y*=(self.get_value("bell_width")-self.d1)
            y+=self.d1
            geo.append([x,y])
        return Geo(geo=geo)

output_dir="projects/temp/test"

if os.path.exists(output_dir):
    shutil.rmtree(output_dir)

print("writing files to " + os.path.abspath(output_dir))

cone=ConeMutationParameter()
mutator=ExploringMutator()

for i in range(10):

    # print(i)
    mutant=cone.copy()
    mutator.mutate(mutant)
    mutant.after_mutate()
    add_bubble=AddBubble(mutant.make_geo())
    mutator.mutate(add_bubble)
    add_bubble.after_mutate()
    print(add_bubble)
    
    geo=add_bubble.make_geo()
    visualize_geo_to_files(geo, output_dir, "cone" + str(i))
    break

#    if i==0:
    
    