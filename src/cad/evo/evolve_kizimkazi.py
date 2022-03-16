# kizimkazi has two singer notes

from cad.calc.pipeline import Pipeline, ExplorePipelineStep, OptimizeGeoStep, PipelineStartStep, FinetuningPipelineStep, AddPointOptimizerExplore, AddPointOptimizerFinetune
from cad.common.app import App
from cad.calc.mutation import ExploringMutator, FinetuningMutator, MutantPool
from cad.calc.parameters import MatemaShape
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

if __name__=="__main__":
    try:
        App.full_init("evolve_kizimkazi")

        losslogger=LossCADLogger()

        fundamental=-31
        fundamental_freq=note_to_freq(fundamental)
        
        length=1168.6795199638118

        wavelength_fundamental=freq_to_wavelength(fundamental_freq)
        wavelength_2nd_harmonic=freq_to_wavelength(fundamental_freq*3)
        wavelength_4nd_harmonic=freq_to_wavelength(fundamental_freq*5)

        max_fundamental=math.sin(length*2*np.pi/wavelength_fundamental)
        max_2nd_harmonic=math.sin(length*2*np.pi/wavelength_2nd_harmonic)
        max_4nd_harmonic=math.sin(length*2*np.pi/wavelength_4nd_harmonic)
        logging.info(f"fundamental\t{max_fundamental}")
        logging.info(f"2nd harmonic\t{max_2nd_harmonic}")
        logging.info(f"4th harmonic\t{max_4nd_harmonic}")

        target_peaks=[fundamental_freq*3, fundamental_freq*5]

        loss=MbeyaLoss(fundamental=fundamental, target_peaks=target_peaks, n_notes=3)    
        father=MatemaShape(n_bubbles=1, add_bubble_prob=0.3)

        initial_pool=MutantPool.create_from_father(father, App.get_config()["n_poolsize"], loss)

        pipeline=Pipeline()

        pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool, n_generations=200, generation_size=70))
        pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss, n_generations=500, generation_size=30))

        for i in range(10):
            pipeline.add_step(AddPointOptimizerExplore(loss, n_generations=100, generation_size=30))
            pipeline.add_step(AddPointOptimizerFinetune(loss, n_generations=100, generation_size=30))

        ui=EvolutionUI()

        pipeline.run()

    except Exception as e:
        App.log_exception(e)
