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
from cad.calc.parameters import MutationParameterSet, MutationParameter
import pandas as pd
from cad.calc.util.cad_logger import LossCADLogger
import logging
import sys
import logging
import json
from cad.calc.loss import LossFunction
from cad.ui.evolution_ui import EvolutionUI

# loss function
class MaveiraLoss(LossFunction):

    def __init__(self):
        self.reference = '{"note": {"0": "F#1", "1": "F#2", "9": "C#3", "2": "F#3", "3": "A#4", "5": "C#4", "6": "E4", "8": "F#4", "7": "G#4", "4": "A#5"}, "cent-diff": {"0": 10.976304776706769, "1": 4.430988666177171, "9": 4.6550114353010486, "2": 7.700553470020566, "3": 22.041494197620892, "5": 6.836781162076733, "6": 38.40718809456689, "8": 7.700553470020566, "7": 5.609648312064053, "4": 20.732432472438944}, "freq": {"0": 91.91400470014798, "1": 184.52432761772133, "9": 276.4383323178693, "2": 368.3523370180173, "3": 460.2663417181653, "5": 552.1803464183132, "6": 644.7906693358866, "8": 736.7046740360346, "7": 827.9223605187572, "4": 921.2290016537559}, "impedance": {"0": 212703466.9937342, "1": 51360481.26009979, "9": 4189237.0021876707, "2": 43956280.82140037, "3": 41948922.38472426, "5": 31435813.59818078, "6": 23187543.30085413, "8": 7746036.080585161, "7": 9296255.857709624, "4": 40586857.56672239}}'
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

        fundamental_loss = tuning_loss[0]*3
        tuning_loss = np.sum(tuning_loss)*3
        imp_loss = np.sum(imp_loss)
        
        return {
            "loss": fundamental_loss + tuning_loss + imp_loss,
            "fundamental_loss": fundamental_loss,
            "tuning_loss": tuning_loss,
            "imp_loss": imp_loss
        }
    
# shape
class MaveiraShape(MutationParameterSet):
    
    def __init__(self):
        
        MutationParameterSet.__init__(self)

        self.d1=32
        self.n_segments = 15
        
        self.add_param("length", 1250, 1440)
        self.add_param("bellsize", 90, 110)
        self.add_param("power", 1,2)
        
        for i in range(self.n_segments-1):
            self.add_param(f"delta_x{i}", -20, 20)
            self.add_param(f"delta_y{i}", 0.8, 1.2)
        

    def make_geo(self):
        length = self.get_value("length")
        bellsize = self.get_value("bellsize")

        x = length*np.arange(self.n_segments+1)/self.n_segments
    
        y= np.arange(self.n_segments+1)/self.n_segments
        p = self.get_value("power")
        y = np.power(y, p)
        y = np.power(y, p)
        y = np.power(y, p)
        y = self.d1 + y*(bellsize - self.d1)
        
        for i in range(1, self.n_segments-1):
            delta_x = self.get_value(f"delta_x{i}")
            delta_y = self.get_value(f"delta_y{i}")
            y[i] *= delta_y
            x[i] += delta_x
            x = sorted(x)
            
        geo = list(zip(x,y))
        
        return Geo(geo)


if __name__=="__main__":
    try:
        App.full_init("evolve_maveira")

        losslogger=LossCADLogger()

        loss=MaveiraLoss()    
        father=MaveiraShape()
        initial_pool=MutantPool.create_from_father(father, App.get_config()["n_poolsize"], loss)

        pipeline=Pipeline()

        pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool, n_generations=200, generation_size=70))
        pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss, n_generations=500, generation_size=30))

        ui=EvolutionUI()

        pipeline.run()

    except Exception as e:
        App.log_exception(e)
