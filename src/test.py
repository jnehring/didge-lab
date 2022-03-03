from cad.common.app import App
import numpy as np
from cad.calc.geo import geotools
from cad.calc.conv import note_to_freq, note_name, freq_to_note_and_cent
import math
import numpy as np
from cad.calc.geo import Geo
import matplotlib.pyplot as plt
from cad.calc.parameters import FinetuningParameters, MutationParameterSet, MbeyaShape, MatemaShape
import random
from cad.cadsd.cadsd import CADSD, cadsd_volume
from cad.cadsd._cadsd import cadsd_Ze, create_segments_from_geo
from cad.ui.visualization import make_didge_report, DidgeVisualizer
import seaborn as sns
import pandas as pd
from cad.calc.parameters import AddBubble, MbeyaShape
from cad.calc.mutation import ExploringMutator
from make_didge_report import didge_report
import os
from cad.calc.loss import LossFunction, TootTuningHelper, single_note_loss, diameter_loss
import pickle
import json
from cad.evo.evolve_matema import MatemaLoss

# shape=MatemaShape(n_bubbles=2, add_bubble_prob=0.4)
# shape.read_csv("test.csv")
# shape.make_geo()

infile="output/2022-03-03T12-03-10_default/results/5.pkl"

mutant=pickle.load(open(infile, "rb"))

print(mutant.get(9).geo.get_cadsd().get_notes())
# mutant.get(0).parameterset.to_pandas().to_csv("test.csv")

# print(mutant.get(8).parameterset)

# for i in range(10):
#    print(i, mutant.get(i).geo.geo[-1][0])

# shape=MatemaShape(n_bubbles=2, add_bubble_prob=0.4)
# shape.read_csv("test.csv")

# ol=1847.567267735626
# shape.set_minmax("length", ol, ol)

# em=ExploringMutator()
# for i in range(20):
#     mutant=shape.copy()
#     em.mutate(mutant)
#     print(mutant.make_geo().geo[-1])