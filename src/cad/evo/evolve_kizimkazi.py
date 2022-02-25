# kizimkazi has many toots

from cad.calc.pipeline import Pipeline, ExplorePipelineStep, OptimizeGeoStep, PipelineStartStep, FinetuningPipelineStep, AddPointOptimizerExplore, AddPointOptimizerFinetune
from cad.common.app import App
from cad.calc.mutation import ExploringMutator, FinetuningMutator, MutantPool
from cad.calc.parameters import MbeyaShape
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

try:
    App.full_init("evolve_kizimkazi")

    losslogger=LossCADLogger()

    class KizimkaziLoss(LossFunction):

        def __init__(self, target_balance):
            LossFunction.__init__(self)
            self.tuning_helper=TootTuningHelper([0,2,3,7,9,10], -31)
            self.target_balance=target_balance

        def get_loss(self, geo, context=None):

            fundamental=single_note_loss(-31, geo)*4
            octave=single_note_loss(-19, geo, i_note=1)

            tuning_deviations=self.tuning_helper.get_tuning_deviations(geo)
            for i in range(len(tuning_deviations)):
                tuning_deviations[i]*=tuning_deviations[i]
            tuning_loss=sum(tuning_deviations)*5

            d_loss = diameter_loss(geo)*0.1

            final_loss=tuning_loss + d_loss + fundamental + octave

            return {
                "loss": final_loss,
                "tuning_loss": tuning_loss,
                "diameter_loss": d_loss,
                "fundamental_loss": fundamental,
                "octave_loss": octave,
            }
            return final_loss

    loss=IringaLoss(open_didge_balance)    
    father=MbeyaShape()
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
