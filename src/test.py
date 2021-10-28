from cad.calc.didgmo import PeakFile, didgmo_bridge, cleanup
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
from cad.calc.parameters import BasicShapeParameters, MutationParameterSet, MutationParameter
from cad.calc.htmlreport import make_html_report

class TestParameter(MutationParameterSet):
    
    def __init__(self):
        super(TestParameter, self).__init__()
        self.mutable_parameters.append(MutationParameter("test", 0, -2, 2))
        self.mutable_parameters.append(MutationParameter("test2", 0, -2, 2))

    def make_geo(self):
        pass

p=TestParameter()
em=FinetuningMutator(learning_rate=1)

for i in range(10):
    em.mutate(p)
    print(p)

