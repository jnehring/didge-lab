# matema is in d, plays a minor scale and has a singer note at a - 440 Hz

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

class SintraLoss(LossFunction):
        
    def __init__(self):
        LossFunction.__init__(self)
        
        base_note = -31
        self.target_notes = base_note + np.concatenate([np.array((0,4,7)) + 12*n for n in range(0,5)])
        self.target_freqs = np.log2(note_to_freq(self.target_notes))
        #self.multiples = np.arange(1,15)*note_to_freq(base_note)

    def get_deviations(self, freq, reference):
        
        deviations = []
        for f in freq:
            d = [np.abs(r-f) for r in reference]
            deviations.append(np.min(d))
        return deviations
        
    def get_loss(self, geo, context=None):
        
        notes = geo.get_cadsd().get_notes()
        freqs = np.log2(list(notes.freq))
        toots = freqs
        
        deviations = self.get_deviations(toots, self.target_freqs)
        fundamental_loss = deviations[0]
        fundamental_loss *= 3
        toots_loss = np.sum(deviations[1:] / np.arange(1, len(deviations[1:])+1))
        toots_loss *= 1

        imp = geo.get_cadsd().get_impedance_spektrum()
        low = (imp.query("freq<400")).impedance.sum()
        high = (imp.query("freq>=400")).impedance.sum()
        brightness_loss = -1*high/low
        brightness_loss += 1

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

    loss=SintraLoss()
    father=NazareShape()
    initial_pool=MutantPool.create_from_father(father, 20, loss)

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
