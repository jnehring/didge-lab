from cad.calc.pipeline import Pipeline, ExplorePipelineStep, OptimizeGeoStep, PipelineStartStep, FinetuningPipelineStep, AddPointOptimizerExplore, AddPointOptimizerFinetune
from cad.common.app import App
from cad.calc.mutation import ExploringMutator, FinetuningMutator, MutantPool
from cad.calc.parameters import MbeyaShape
from cad.calc.loss import LossFunction, TootTuningHelper, diameter_loss
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
    App.full_init("evolve_penta")

    geo=[[0,32], [800,32], [900,38], [970,42], [1050, 40], [1180, 48], [1350, 60], [1390, 68], [1500, 72]]
    geo=Geo(geo)
    open_didge_balance=cadsd_octave_tonal_balance(geo)

    losslogger=LossCADLogger()

    class MbeyaLoss(LossFunction):

        def __init__(self, target_balance):
            LossFunction.__init__(self)
            self.tuning_helper=TootTuningHelper([0,3,7, 10], -31)
            self.target_balance=target_balance

        def get_loss(self, geo, context=None):

            tuning_deviations=self.tuning_helper.get_tuning_deviations(geo)
            tuning_deviations[0]*=2
            for i in range(len(tuning_deviations)):
                tuning_deviations[i]*=tuning_deviations[i]
            tuning_loss=sum(tuning_deviations)*10

            n_notes=len(tuning_deviations)
            n_note_loss=0
            if n_notes<3:
                n_note_loss=0.1
            elif n_notes==4:
                n_note_loss=-0.1
            elif n_notes>4:
                n_note_loss=-0.2

            balance_loss=0
            balance=cadsd_octave_tonal_balance(geo)

            d_loss = diameter_loss(geo)

            for i in range(len(balance)):
                balance_loss += abs(balance[i]-self.target_balance[i])

            final_loss=balance_loss + tuning_loss + n_note_loss + d_loss

            return {
                "loss": final_loss,
                "balance_loss": balance_loss,
                "tuning_loss": tuning_loss,
                "n_note_loss": n_note_loss,
                "diameter_loss": d_loss
            }
            return final_loss

    loss=MbeyaLoss(open_didge_balance)    
    father=MbeyaShape()
    initial_pool=MutantPool.create_from_father(father, App.get_config()["n_poolsize"], loss)

    pipeline=Pipeline()

    pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool, n_generations=100, generation_size=70))
    pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss, n_generations=50, generation_size=30))
    pipeline.add_step(AddPointOptimizerExplore(loss, n_generations=50, generation_size=30))
    pipeline.add_step(AddPointOptimizerFinetune(loss, n_generations=50, generation_size=30))
    pipeline.add_step(AddPointOptimizerExplore(loss, n_generations=50, generation_size=30))
    pipeline.add_step(AddPointOptimizerFinetune(loss, n_generations=50, generation_size=30))
    pipeline.add_step(AddPointOptimizerExplore(loss, n_generations=50, generation_size=30))
    pipeline.add_step(AddPointOptimizerFinetune(loss, n_generations=50, generation_size=30))

    ui=EvolutionUI()

    pipeline.run()

except Exception as e:
    App.log_exception(e)
