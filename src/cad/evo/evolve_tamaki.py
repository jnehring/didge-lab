from cad.calc.pipeline import Pipeline, ExplorePipelineStep, OptimizeGeoStep, PipelineStartStep, FinetuningPipelineStep, AddPointOptimizerExplore, AddPointOptimizerFinetune
from cad.common.app import App
from cad.calc.mutation import ExploringMutator, FinetuningMutator, MutantPool
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
from scipy.signal import argrelextrema
import os
from cad.calc.geo import Geo
from cad.calc.conv import freq_to_note_and_cent, note_name
import pandas as pd
import seaborn as sns
from cad.calc.parameters import MutationParameterSet, MutationParameter, TamakiShape
import pandas as pd
from cad.calc.util.cad_logger import LossCADLogger
import logging
import sys
import logging
import json
from cad.calc.loss import LossFunction
from cad.ui.evolution_ui import EvolutionUI

# loss function
class TamakiLoss(LossFunction):

    def __init__(self):
        self.reference = '{"note": {"0": "D1", "7": "D2", "3": "G2", "6": "A#3", "1": "D#3", "5": "F#3", "4": "A#4", "2": "C4", "8": "E4", "9": "A#5"}, "cent-diff": {"0": -29.186907488181646, "7": -29.186907488181646, "3": -11.705039773796244, "6": 28.121293338425346, "1": 40.170981983253284, "5": -40.057544424674774, "4": 48.36987561570183, "2": -32.98842874872534, "8": 8.621592573854997, "9": 38.215981117865994}, "freq": {"0": 74.66440923932761, "7": 149.32881847865522, "3": 197.32736727536582, "6": 229.32639980650623, "1": 303.9908090458338, "5": 378.6552182851614, "4": 453.319627524489, "2": 533.3172088523401, "8": 655.9801668883782, "9": 911.9724271375014}, "impedance": {"0": 7077269.224123592, "7": 651051.9652029042, "3": 1254565.572641898, "6": 653668.1255613645, "1": 3621993.552801448, "5": 783622.9325813947, "4": 991882.236723337, "2": 2645503.3839946836, "8": 590509.1527637121, "9": 433782.7710599926}}'
        self.reference = pd.DataFrame(json.loads(self.reference))        
        self.reference["impedance_normalized"] = self.reference.impedance / self.reference.impedance.max()
        self.reference["logfreq"] = np.log2(self.reference.freq)
        
    def get_loss(self, geo):
        peaks = geo.get_cadsd().get_notes()
        peaks["logfreq"] = np.log2(peaks.freq)
        peaks["impedance_normalized"] = peaks.impedance / peaks.impedance.max()
        
        tuning_loss = []
        imp_loss = []
        for ix, peak in peaks.iterrows():
            mini = np.argmin([np.abs(peak.logfreq-f) for f in self.reference.logfreq])
            
            tl = np.abs(peak.logfreq-self.reference.logfreq[mini])
            il = np.abs(peak.impedance_normalized - self.reference.impedance_normalized[mini])
            tuning_loss.append(tl)
            imp_loss.append(il)
            # print(f"{self.reference.freq[mini]:.0f}, {peak.freq:.0f}, {tl:.2f}, {il:.2f}")

        fundamental_loss = tuning_loss[0]*10
        tuning_loss = np.sum(tuning_loss)
        imp_loss = np.sum(imp_loss)
        
        return {
            "loss": fundamental_loss + tuning_loss + imp_loss,
            "fundamental_loss": fundamental_loss,
            "tuning_loss": tuning_loss,
            "imp_loss": imp_loss
        }
        
if __name__=="__main__":
    try:
        App.full_init("evolve_tamaki")

        losslogger=LossCADLogger()

        loss=TamakiLoss()    
        father=TamakiShape()
        initial_pool=MutantPool.create_from_father(father, App.get_config()["n_poolsize"], loss)

        pipeline=Pipeline()

        pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool, n_generations=200, generation_size=70))
        pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss, n_generations=500, generation_size=30))

        ui=EvolutionUI()

        pipeline.run()

    except Exception as e:
        App.log_exception(e)
