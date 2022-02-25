# matema has two very strong peaks in the ground tone spektrum that play a chord

from cad.calc.pipeline import Pipeline, ExplorePipelineStep, OptimizeGeoStep, PipelineStartStep, FinetuningPipelineStep, AddPointOptimizerExplore, AddPointOptimizerFinetune
from cad.common.app import App
from cad.calc.mutation import ExploringMutator, FinetuningMutator, MutantPool
from cad.calc.parameters import MbeyaShape
from cad.calc.loss import LossFunction, TootTuningHelper, diameter_loss, single_note_loss, ImpedanceVolumeLoss
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
import json

class MatemaLoss(LossFunction):

    def __init__(self):
        LossFunction.__init__(self)
        self.base_note=-31
        frequencies=[]
        f=note_to_freq(-31)
        while f<1000:
            frequencies.append(f)
            f*=2
        self.singer_tuning_helper=TootTuningHelper(frequencies=frequencies, filter_rel_imp=0.9, min_freq=350)
        self.toot_tuning_helper=TootTuningHelper(fundamental=-31, scale=[0,3,7,10], filter_rel_imp=0.9, max_freq=350)

        self.ground_impedance=ImpedanceVolumeLoss(min_freq=note_to_freq(-32), max_freq=note_to_freq(-30), num_peaks=1)
        self.first_toot_impedance=ImpedanceVolumeLoss(min_freq=note_to_freq(-32), max_freq=250, num_peaks=1)
        self.singer_toot_impedance=ImpedanceVolumeLoss(min_freq=250, num_peaks=1)

    def get_loss(self, geo, context=None):
        
        # fundamental loss
        fundamental=single_note_loss(self.base_note, geo)*4
        #octave=single_note_loss(-19, geo, i_note=1)

        # toot loss
        tuning_deviations, toot_peaks=self.toot_tuning_helper.get_tuning_deviations(geo, return_peaks=True)
        for i in range(len(tuning_deviations)):
            tuning_deviations[i]*=tuning_deviations[i]
        tuning_loss=sum(tuning_deviations)*5
        has_toots_loss=0
        if len(toot_peaks)<2:
            has_toots_loss=10    

        # singer tuning loss
        tuning_deviations, singer_peaks=self.singer_tuning_helper.get_tuning_deviations(geo, return_peaks=True)
        for i in range(len(tuning_deviations)):
            tuning_deviations[i]*=tuning_deviations[i]
        singer_tuning_loss=sum(tuning_deviations)*5

        # diameter loss
        d_loss = diameter_loss(geo)*0.1
    
        # volumes
        ground_volume=self.ground_impedance.get_loss(geo)
        first_toot_impedance=self.first_toot_impedance.get_loss(geo)
        singer_toot_impedance=self.singer_toot_impedance.get_loss(geo)

        losses= {
            "tuning_loss": tuning_loss,
            "diameter_loss": d_loss,
            "fundamental_loss": fundamental,
            "has_toots_loss": has_toots_loss,
            "singer_tuning_loss": singer_tuning_loss,
            "ground_volume": ground_volume,
            "first_toot_impedance": first_toot_impedance,
            "singer_toot_impedance": singer_toot_impedance
        }
        final_loss=sum(losses.values())
        losses["loss"]=final_loss
        return losses

if __name__ == "__main__":
    try:
        loss=MatemaLoss()    

        shape=MbeyaShape(n_bubbles=2, add_bubble_prob=0.4)

        shape.set_minmax("opening_factor_y", 1.5, 2.0)
        shape.set_minmax("d_pre_bell", 0, 10)
        shape.set_minmax("bellsize", 3, 20)

        initial_pool=MutantPool.create_from_father(shape, App.get_config()["n_poolsize"], loss)

        pipeline=Pipeline()

        pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool, n_generations=100, generation_size=70))
        pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss, n_generations=50, generation_size=30))

        for i in range(2):
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
