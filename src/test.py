from cad.calc.mutation import ExploringMutator
from cad.calc.parameters import ConeBubble, ConeMutationParameter, AddBubble
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

output_dir="projects/temp/test"

if os.path.exists(output_dir):
    shutil.rmtree(output_dir)

print("writing files to " + os.path.abspath(output_dir))

father_cone=ConeMutationParameter()
father_bubble=AddBubble(None)
father=ConeBubble(father_cone, father_bubble)
mutator=ExploringMutator()

for i in range(10):

    print(i)
    mutant=father.copy()
    mutator.mutate(mutant)
    mutant.after_mutate()
    
    geo=mutant.make_geo()
    #print(geo.segments_to_str())
    visualize_geo_to_files(geo, output_dir, "cone" + str(i))
    
#    if i==0:
    
    