# mbeya should have the frequency spektrum of the open didgeridoo
# it is tuned in d and has toots in the minor scale

from cad.calc.pipeline import Pipeline, ExplorePipelineStep, OptimizeGeoStep, PipelineStartStep, FinetuningPipelineStep, AddPointOptimizerExplore, AddPointOptimizerFinetune
from cad.common.app import App
from cad.calc.mutation import ExploringMutator, FinetuningMutator, MutantPool
from cad.calc.parameters import MatemaShape
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
    App.full_init("evolve_kendwa")

    losslogger=LossCADLogger()

    class KendwaLoss(LossFunction):

        def __init__(self):
            LossFunction.__init__(self)

            self.base_note=-31
            self.target_freqs=[]

            base_freq=note_to_freq(self.base_note)
            freq=base_freq
            i=1
            while freq<800:
                self.target_freqs.append(freq)
                i+=1
                freq=base_freq*i

        def get_loss(self, geo, context=None):

            fundamental=single_note_loss(self.base_note, geo)*6

            impedance_freq_loss=0
            impedance_vol_loss=0

            notes=geo.get_cadsd().get_notes()
            notes=notes[notes["rel_imp"]>0.15]

            num_notes_loss=max(4-len(notes), 0)
            d_loss = diameter_loss(geo)*0.3

            for ix, note in notes.iterrows():

                diff=[abs(target-note["freq"]) for target in self.target_freqs]
                closest_target_freq=self.target_freqs[np.argmin(diff)]

                f1=math.log(note["freq"], 2)
                f2=math.log(closest_target_freq, 2)
                impedance_freq_loss += math.sqrt(abs(f1-f2))
                impedance_vol_loss += math.sqrt(1/(note["impedance"]/1e6))

            impedance_freq_loss/=len(notes)
            impedance_vol_loss/=len(notes)

            impedance_freq_loss*=8
            impedance_vol_loss*=8
            
            loss = {
                "num_notes_loss": num_notes_loss,
                "diameter_loss": d_loss,
                "fundamental_loss": fundamental,
                "impedance_freq_loss": impedance_freq_loss,
                "impedance_vol_loss": impedance_vol_loss
            }
            loss["loss"]=sum(loss.values())
            return loss

    loss=KendwaLoss()    
    father=MatemaShape()
    initial_pool=MutantPool.create_from_father(father, App.get_config()["n_poolsize"], loss)

    pipeline=Pipeline()

    pipeline.add_step(ExplorePipelineStep(ExploringMutator(), loss, initial_pool, n_generations=500, generation_size=70))
    pipeline.add_step(FinetuningPipelineStep(FinetuningMutator(), loss, n_generations=1000, generation_size=30))

    for i in range(10):
        pipeline.add_step(AddPointOptimizerExplore(loss, n_generations=100, generation_size=30))
        pipeline.add_step(AddPointOptimizerFinetune(loss, n_generations=100, generation_size=30))


    ui=EvolutionUI()

    pipeline.run()

except Exception as e:
    App.log_exception(e)
