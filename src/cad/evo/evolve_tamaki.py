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

def get_harmonic_maxima(freq, spectrum, min_freq=60):
    i=0
    maxima = []
    base_freq = min_freq
    while i*base_freq<1000:
        if i==0:
            window = freq>min_freq
        else:
            window = (freq>(i+0.5)*base_freq) & (freq<base_freq*(i+1.5))

        if window.astype(int).sum() == 0:
            break
        window_f = freq[window]
        window_s = spectrum[window]
        maxi = np.argmax(window_s)
        max_f = window_f[maxi]
        if i==0:
            base_freq=max_f

        maxima.append(max_f)
        i+=1
    return maxima

class TamakiLoss(LossFunction):

    def __init__(self):
        r = {"freq": [6.400585038762361, 7.368876179035023, 7.964485923955688, 8.368876179035023, 8.697202045120536, 8.964485923955687, 9.19895117759271, 9.384817722904044, 9.535234565457143, 9.709913096870089, 9.83702501477343, 9.95383867975618], "amp": [1.0, 0.6073456474120418, 0.7250740308214233, 0.5819491541103495, 0.5757528442270442, 0.7646716809346981, 0.7289892200366962, 0.4648478386222508, 0.6236959507896652, 0.49612524062788294, 0.39607427089021596, 0.5221732266032565], "priorities": [0, 5, 6]}

        self.reference_freq = np.array(r["freq"])
        self.reference_amp = np.array(r["amp"])
        self.reference_priorities = np.array(r["priorities"])
        
    def get_loss(self, geo):
        
        gs = geo.get_cadsd().get_ground_spektrum()
        computed_freqs = np.array(list(gs.keys()))
        computed_amp = np.array(list(gs.values()))
        peaks = get_harmonic_maxima(computed_freqs, computed_amp)
        peaks = np.log2(peaks)
        computed_freqs = np.log2(computed_freqs)
        computed_amp -= computed_amp.min()
        computed_amp /= computed_amp.max()
        
        tuning_loss = 0
        amp_loss = 0
        priority_amp_loss = 0
        fundamental_loss = 0
        
        for i in range(len(self.reference_freq)):
            mini = np.argmin(np.abs(peaks-self.reference_freq[i]))
            closest_freq = peaks[mini]
            closest_freq_index = np.argmin(np.abs(computed_freqs-closest_freq))
            closest_amp = computed_amp[closest_freq_index]
            
            _tuning_loss = np.sqrt(np.power(closest_freq-self.reference_freq[i], 2))
            
            if i in self.reference_priorities:
                priority_amp_loss += 1-closest_amp
                tuning_loss += _tuning_loss*3
            else:
                amp_loss += np.sqrt(np.power(closest_amp-self.reference_amp[i], 2))
                tuning_loss += _tuning_loss
                
            if i==0:
                fundamental_loss = _tuning_loss
                
        tuning_loss /= len(self.reference_freq)
        amp_loss /= len(self.reference_freq)

        geo.get_cadsd().release_memory()
        
        tuning_loss *= 5
        fundamental_loss *= 5
        amp_loss *= 5

        return {
            "loss": fundamental_loss + tuning_loss + amp_loss + priority_amp_loss,
            "fundamental_loss": fundamental_loss,
            "tuning_loss": tuning_loss,
            "amp_loss": amp_loss,
            "priority_amp_loss": priority_amp_loss
        }

if __name__=="__main__":
    try:
        App.full_init("evolve_tamaki")

        losslogger=LossCADLogger()

        loss=TamakiLoss()    
        father=TamakiShape()
        initial_pool=MutantPool.create_from_father(father, App.get_config()["n_poolsize"], loss)

        pipeline=Pipeline()

        pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool, n_generations=500, generation_size=30))
        pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss, n_generations=500, generation_size=30))

        ui=EvolutionUI()

        pipeline.run()

    except Exception as e:
        App.log_exception(e)
