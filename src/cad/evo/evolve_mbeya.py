# mbeya is tuned in d and has toots in the minor scale

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
    App.full_init("evolve_penta")

    losslogger=LossCADLogger()

    class MbeyaLoss(LossFunction):

        def __init__(self):
            LossFunction.__init__(self)

            self.scale=[0,2,3,5,7,9,10]
            self.fundamental=-31

            self.scale_note_numbers=[]
            for i in range(len(self.scale)):
                self.scale_note_numbers.append(self.scale[i]+self.fundamental)

            n_octaves=10
            self.target_peaks=[]
            for note_number in self.scale_note_numbers:
                for i in range(0, n_octaves):
                    transposed_note=note_number+12*i
                    freq=note_to_freq(transposed_note)
                    freq=math.log(freq, 2)
                    self.target_peaks.append(freq)

        def get_loss(self, geo, context=None):

            fundamental=single_note_loss(-31, geo)*4
            octave=single_note_loss(-19, geo, i_note=1)

            notes=geo.get_cadsd().get_notes()
            tuning_loss=0
            volume_loss=0

            if len(notes)>2:
                for ix, note in notes[2:].iterrows():
                    f1=math.log(note["freq"],2)
                    closest_target_index=np.argmin([abs(x-f1) for x in self.target_peaks])
                    f2=self.target_peaks[closest_target_index]
                    tuning_loss += math.sqrt(abs(f1-f2))
                    volume_loss += math.sqrt(1/(note["impedance"]/1e6))
            tuning_loss*=4
            volume_loss*=2
            
            n_note_loss=max(5-len(notes), 0)*5

            d_loss = diameter_loss(geo)*0.1

            loss={
                # "tuning_loss": tuning_loss,
                "tuning_loss": tuning_loss,
                "volume_loss": volume_loss,
                "n_note_loss": n_note_loss,
                "diameter_loss": d_loss,
                "fundamental_loss": fundamental,
                "octave_loss": octave,
            }
            loss["loss"]=sum(loss.values())
            return loss

    loss=MbeyaLoss()    
    father=MbeyaShape()
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
