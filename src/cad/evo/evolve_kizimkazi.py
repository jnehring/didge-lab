# kizimkazi has two singer notes

from cad.calc.pipeline import Pipeline, ExplorePipelineStep, OptimizeGeoStep, PipelineStartStep, FinetuningPipelineStep, AddPointOptimizerExplore, AddPointOptimizerFinetune
from cad.common.app import App
from cad.calc.mutation import ExploringMutator, FinetuningMutator, MutantPool
from cad.calc.parameters import KizimkaziShape
from cad.calc.loss import LossFunction, TootTuningHelper, diameter_loss, single_note_loss
import numpy as np
from cad.calc.geo import geotools
from cad.cadsd.cadsd import CADSD, cadsd_octave_tonal_balance
from cad.calc.conv import note_to_freq, note_name, freq_to_note_and_cent
import math
import numpy as np
from cad.calc.geo import Geo
from cad.ui.evolution_ui import EvolutionUI
from cad.calc.util.losslog import LossLog
from cad.calc.util.cad_logger import LossCADLogger
import logging
import sys

try:
    App.full_init("evolve_kizimkazi")

    losslogger=LossCADLogger()

    class KizimkaziLoss(LossFunction):

        def __init__(self,):
            LossFunction.__init__(self)

            self.base_note=-31

            self.notes=[]

            for i in range(5):
                self.notes.append(self.base_note + 4 + i*12)
                self.notes.append(self.base_note + 7 + i*12)

            self.notes=[note_to_freq(x) for x in self.notes]
            
        def get_loss(self, geo, context=None):

            fundamental=single_note_loss(self.base_note, geo)*5
            octave=single_note_loss(self.base_note+12, geo, i_note=1)

            peaks=geo.get_cadsd().get_notes().copy()
            singer_tuning_loss=0
            singer_volume_loss=0
            peaks=geo.
            for target_freq in self.target_peaks:
                peaks["diff"]=abs(peaks.freq-target_freq)
                closest_peak=peaks[peaks["diff"]==peaks["diff"].min()].iloc[0]

                f1=math.log(target_freq, 2)
                f2=math.log(closest_peak["freq"], 2)
                singer_tuning_loss += math.sqrt(abs(f1-f2))

                singer_volume_loss += math.sqrt(1/(closest_peak["impedance"]/1e6))
            singer_tuning_loss*=4
            singer_volume_loss*=2

            d_loss=diameter_loss(geo)


            loss["loss"]=sum(loss.values())

            return loss

    loss=KizimkaziLoss()    
    father=KizimkaziShape(1462)
    father.make_geo()
    sys.exit(0)
    initial_pool=MutantPool.create_from_father(father, App.get_config()["n_poolsize"], loss)

    pipeline=Pipeline()

    pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool, n_generations=100, generation_size=70))
    pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss, n_generations=50, generation_size=30))

    for i in range(10):
        pipeline.add_step(AddPointOptimizerExplore(loss, n_generations=100, generation_size=30))
        pipeline.add_step(AddPointOptimizerFinetune(loss, n_generations=100, generation_size=30))
        pipeline.add_step(AddPointOptimizerExplore(loss, n_generations=100, generation_size=30))
        pipeline.add_step(AddPointOptimizerFinetune(loss, n_generations=100, generation_size=30))
        pipeline.add_step(AddPointOptimizerExplore(loss, n_generations=100, generation_size=30))
        pipeline.add_step(AddPointOptimizerFinetune(loss, n_generations=100, generation_size=30))

    ui=EvolutionUI()

    pipeline.run()

except Exception as e:
    App.log_exception(e)
