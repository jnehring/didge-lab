from cad.common.app import App
import numpy as np
from cad.calc.geo import geotools
from cad.calc.conv import note_to_freq, note_name, freq_to_note_and_cent, freq_to_wavelength
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
from cad.calc.parameters import MatemaShape
from cad.evo.evolve_kizimkazi import KizimkaziLoss
from cad.calc.util.mutant_pool_store import save_mutant_pool

# open didge
geo=[[0,32], [800,32], [900,38], [970,42], [1050, 40], [1180, 48], [1350, 60], [1390, 68], [1500, 72]]
geo=Geo(geo)

geos=[]
parameters=[]
losses=[]

if options.single>=0:
    mpe=pool.get(options.single)
    geos.append(mpe.geo)
    losses.append(mpe.loss)
    parameters.append(mpe.parameterset)

    didge_report(geos, outdir, overview_report=None, parameters=parameters, losses=losses)
