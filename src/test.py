from cad.calc.didgmo import PeakFile, didgmo_bridge
from cad.calc.visualization import DidgeVisualizer, FFTVisualiser, visualize_geo_fft
import matplotlib.pyplot as plt
from cad.calc.conv import note_to_freq, note_name, freq_to_note
from cad.calc.geo import Geo
from IPython.display import clear_output
import math
import random
import copy
from tqdm import tqdm
from cad.calc.loss import ScaleLoss, AmpLoss, CombinedLoss
from cad.calc.mutation import *
from cad.calc.parameters import BasicShapeParameters
from cad.calc.htmlreport import make_html_report

# python -m algos.evolve_penta

loss=CombinedLoss(
    [ScaleLoss(scale=[0,3,5,7,10], fundamental=-31, n_peaks=8), AmpLoss(n_peaks=8)],
    [10.0, 0.1]
)

bsp=BasicShapeParameters()

mutate_explore_then_finetune(loss=loss, parameters=BasicShapeParameters(), n_poolsize=10, n_explore_iterations=500, n_finetune_iterations=200)
#pool, losses=mutate_explore_then_finetune(loss=loss, parameters=BasicShapeParameters(), n_poolsize=3, n_explore_iterations=10, n_finetune_iterations=10)

#outdir="projects/penta"

#make_html_report(pool, losses, outdir)
# visualize_geo_fft(geo.make_geo(), None, dir=outdir)