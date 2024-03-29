from cad.calc.pipeline import Pipeline, ExplorePipelineStep, OptimizeGeoStep, PipelineStartStep
from cad.common.app import App
from cad.calc.mutation import ExploringMutator, FinetuningMutator, MutantPool
from cad.calc.parameters import ConeMutationParameter, AddBubble, ConeBubble, BasicShapeParameters, IringaShape, EvolveGeoParameter
from cad.calc.loss import LossFunction, TootTuningHelper
import numpy as np
from cad.calc.geo import geotools
from cad.cadsd.cadsd import CADSD, cadsd_octave_tonal_balance
from cad.calc.conv import note_to_freq, note_name, freq_to_note_and_cent
import math
import numpy as np
from cad.calc.geo import Geo
from cad.ui.evolution_ui import EvolutionUI
from cad.calc.util.losslog import LossLog
try:
    App.full_init()

    geo=[[0,32], [800,32], [900,38], [970,42], [1050, 40], [1180, 48], [1350, 60], [1390, 68], [1500, 72]]
    geo=Geo(geo)
    open_didge_balance=cadsd_octave_tonal_balance(geo)

    class OpenDidgeLoss(LossFunction):

        def __init__(self, target_balance):
            LossFunction.__init__(self)
            self.tuning_helper=TootTuningHelper([0,3,7], -31)
            self.target_balance=target_balance

        def get_loss(self, geo):

            tuning_deviations=self.tuning_helper.get_tuning_deviations(geo)
            tuning_deviations[0]*=2
            for i in range(len(tuning_deviations)):
                tuning_deviations[i]*=tuning_deviations[i]
            tuning_loss=sum(tuning_deviations)

            balance_loss=0
            balance=cadsd_octave_tonal_balance(geo)

            for i in range(len(balance)):
                balance_loss += abs(balance[i]-self.target_balance[i])

            return balance_loss + tuning_loss

    loss=OpenDidgeLoss(open_didge_balance)    
    father=EvolveGeoParameter(geo)
    initial_pool=MutantPool.create_from_father(father, App.get_config()["n_poolsize"], loss)

    pipeline=Pipeline()

    pipeline.add_step(PipelineStartStep(initial_pool))
    pipeline.add_step(OptimizeGeoStep(loss))

    ui=EvolutionUI()

    pipeline.run()

except Exception as e:
    App.log_exception(e)