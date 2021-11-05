from cad.calc.loss import ScaleLoss, AmpLoss, CombinedLoss
from cad.calc.mutation import mutate_explore_then_finetune, evolve_explore, Reporter, evolve_finetune, Evolver, FinetuningMutator, ScaleLoggingCallback
from cad.calc.parameters import BasicShapeParameters, MutationParameterSet, MutationParameter,BubbleParameters,  MultiBubble
from cad.calc.report import make_html_report, geo_report
from cad.calc.visualization import visualize_scales_multiple_shapes
import pickle
import logging

import math
from cad.calc.geo import Geo
from cad.calc.didgmo import didgmo_bridge
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


# run it:
# python -m algos.evolve_penta



n_peaks=5
loss=CombinedLoss(
    [ScaleLoss(scale=[0,3,5,7,10], fundamental=-31, n_peaks=n_peaks, octave=True),
    AmpLoss(n_peaks=n_peaks)],
    [10.0, 0.1]
)
father=BasicShapeParameters()

n_explore_iterations=5000
n_finetune_iterations=300
n_poolsize=10
#total=n_explore_iterations+n_poolsize*n_finetune_iterations
total=n_poolsize*n_finetune_iterations
pickle_file="projects/temp/mutants.pickle"

reporter=Reporter(n_explore_iterations)
reporter=Reporter(n_explore_iterations)
reporter.register_callback(500, ScaleLoggingCallback())

mutants=evolve_explore(loss, father, n_poolsize, n_explore_iterations, n_threads=4, reporter=reporter)
pickle.dump(mutants, open(pickle_file, "wb"))
fft=didgmo_bridge(mutants[0]["mutant"].make_geo())
print(fft.peaks)

mutants=pickle.load(open(pickle_file, "rb"))
print(loss.get_loss(mutants[0]["mutant"].make_geo()))

# geo=mutants[0]["mutant"].make_geo()
# fathers=[]
# n_threads=4
# n_bubbles=4
# for i in range(n_threads):
#     mb=MultiBubble(geo, n_bubbles)
#     pos=list(range(1,n_bubbles+1))
#     pos=[x/n_bubbles - 0.5/n_bubbles for x in pos]
#     mb.set_values("pos", pos)
#     fathers.append({"mutant": mb, "loss": 0})

# e=Evolver(fathers[0]["mutant"], loss, FinetuningMutator(learning_rate=0.5), 50, show_progress=True)
# e.run()

# outdir="projects/penta"

# #make_html_report(mutants, outdir)
