# nazare is a copy of the opendidge, with a boost of frequencies between 400 and 800 HZ

from cad.calc.pipeline import Pipeline, ExplorePipelineStep, OptimizeGeoStep, PipelineStartStep, FinetuningPipelineStep, AddPointOptimizerExplore, AddPointOptimizerFinetune
from cad.common.app import App
from cad.calc.mutation import ExploringMutator, FinetuningMutator, MutantPool
from cad.calc.parameters import MbeyaShape
from cad.evo.evolve_mbeya import MbeyaLoss
from cad.calc.loss import LossFunction, TootTuningHelper, diameter_loss, single_note_loss
import numpy as np
from cad.calc.geo import geotools
from cad.cadsd.cadsd import CADSD, cadsd_octave_tonal_balance
from cad.calc.conv import note_to_freq, note_name, freq_to_note_and_cent, freq_to_wavelength
import math
import numpy as np
from cad.calc.geo import Geo
from cad.ui.evolution_ui import EvolutionUI
from cad.calc.util.losslog import LossLog
from cad.calc.util.cad_logger import LossCADLogger
import logging
import sys
import logging
from cad.calc.parameters import MutationParameterSet, NazareShape

class NazareLoss(LossFunction):
        
    def __init__(self):
        LossFunction.__init__(self)
        
        base_note = -31
        self.target_notes = np.array([0,16,24])+base_note
        self.target_freqs = np.log2(note_to_freq(self.target_notes))

        opendidge = [[0,32], [800,32], [900,38], [970,42], [1050, 40], [1180, 48], [1350, 60], [1390, 68], [1500, 72]]
        self.base_brightness = self.get_brightness(Geo(opendidge))
        # self.multiples = np.arange(1,15)*note_to_freq(base_note)

    def get_brightness(self, geo):
        return geo.get_cadsd().get_impedance_spektrum().query("freq>=400 and freq<=800").impedance.sum()

    def get_deviations(self, freq, reference):
        
        deviations = []
        for f in freq:
            d = [np.abs(r-f) for r in reference]
            deviations.append(np.min(d))
        return deviations
        
    def get_loss(self, geo, context=None):
        
        notes = geo.get_cadsd().get_notes()
        freqs = np.log2(list(notes.freq))
        toots = freqs[0:3]
        others = freqs[3:]
        
        deviations = self.get_deviations(toots, self.target_freqs)
        fundamental_loss = deviations[0]
        fundamental_loss *= 30
        toots_loss = np.sum(deviations[1:])/2
        toots_loss *= 10

        brightness_loss = self.base_brightness / self.get_brightness(geo)
        brightness_loss *= 2
        
        loss = {
            "loss": fundamental_loss + toots_loss + brightness_loss,
            "fundamental_loss": fundamental_loss,
            "toots_loss": toots_loss,
            "brightness_loss": brightness_loss
        }
        return loss
    
try:
    App.full_init("evolve_sintra")

    losslogger=LossCADLogger()

    loss=NazareLoss()
    father=NazareShape()
    initial_pool=MutantPool.create_from_father(father, 10, loss)

    pipeline=Pipeline()

    pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool, n_generations=200, generation_size=70))
    pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss, n_generations=100, generation_size=200))

    #for i in range(10):
    #    pipeline.add_step(AddPointOptimizerExplore(loss, n_generations=100, generation_size=30))
    #    pipeline.add_step(AddPointOptimizerFinetune(loss, n_generations=100, generation_size=30))

    ui=EvolutionUI()

    pipeline.run()

except Exception as e:
    App.log_exception(e)
