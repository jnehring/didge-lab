from cad.common.app import App
import numpy as np
from cad.calc.geo import geotools
from cad.calc.conv import note_to_freq, note_name, freq_to_note_and_cent
import math
import numpy as np
from cad.calc.geo import Geo
import matplotlib.pyplot as plt
from cad.calc.parameters import FinetuningParameters, MutationParameterSet, MbeyaShape
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

class MatemaLoss(LossFunction):

    def __init__(self):
        LossFunction.__init__(self)
        self.tuning_helper=TootTuningHelper([0,3,7, 10], -31)

    def get_loss(self, geo, context=None):
        
        fundamental=single_note_loss(-31, geo)*4
        octave=single_note_loss(-19, geo, i_note=1)

        tuning_deviations=self.tuning_helper.get_tuning_deviations(geo)
        for i in range(len(tuning_deviations)):
            tuning_deviations[i]*=tuning_deviations[i]
        tuning_loss=sum(tuning_deviations)*5

        d_loss = diameter_loss(geo)*0.1
    
        # singer loss
        ground_peaks=geo.get_cadsd().get_ground_peaks()

        base_peak=ground_peaks[ground_peaks.freq==ground_peaks.freq.min()].iloc[0]["impedance"]
        singer_peaks=ground_peaks[(ground_peaks.freq>450) & (ground_peaks.freq<=800)]

        if len(singer_peaks)<2:
            singer_volume_loss==-10
            singer_tuning_loss==-10
        else:
            singer_tuning_loss=0
            singer_volume_loss=0

        imp=0
        if len(singer_peaks)>2:
            imp=list(singer_peaks.impedance.sort_values())[-2]

        singer_peaks=singer_peaks[singer_peaks.impedance>=imp].copy()
        singer_peaks["rel_imp"]=singer_peaks.impedance/base_peak
        
        for ix, row in singer_peaks.iterrows():
            freq=row["freq"]
            singer_tuning_loss += self.tuning_helper.get_tuning_deviation_freq(freq)/2
            singer_volume_loss += -1*row["rel_imp"]

        singer_tuning_loss*=3
        singer_volume_loss*=5

        final_loss=tuning_loss + d_loss + fundamental + octave + singer_volume_loss + singer_tuning_loss

        return {
            "loss": final_loss,
            "tuning_loss": tuning_loss,
            "diameter_loss": d_loss,
            "fundamental_loss": fundamental,
            "octave_loss": octave,
            "singer_volume_loss": singer_volume_loss,
            "singer_tuning_loss": singer_tuning_loss
        }
        return final_loss

loss=MatemaLoss()
shape=MbeyaShape(n_bubbles=1, add_bubble_prob=0.1)

geos=[]
parameters=[]
notes=[]
losses=[]
outdir="output/test"
for i in range(5):
    shape.set("d_pre_bell", i*5)
    shape.set("bellsize", i*5)
    parameters.append(shape.copy())
    geo=shape.make_geo()
    geos.append(geo)
    losses.append(loss.get_loss(geo))

#didge_report(geos, outdir, parameters=parameters,contents="spektra,general,notes",losses=losses)